"""
Agent v2 - Tool Executor

Đây là lớp thực thi các tools mà agent gọi.
Tất cả methods BỌC các function/repo sẵn có — KHÔNG sửa code cũ.

Pattern: executor nhận args từ LLM và dispatch đến đúng function.
"""

import json
import traceback
from typing import Optional

from openai import OpenAI

from app.ai.ai_helper import AI
from app.repo.job_qdrant_repo import JobQdrantRepository
from app.agent.prompts import (
    SKILL_GAP_ANALYSIS_PROMPT,
    ROADMAP_GENERATION_PROMPT,
    EVALUATION_PROMPT,
)
import constant.ai as ai_constant
import constant.config as cfg
from pkg.logging import logger


class ToolExecutor:
    """
    Executes agent tool calls by delegating to existing repo/AI classes.
    All existing code is untouched — this class only WRAPS them.
    """

    def __init__(self):
        self.ai = AI()
        self.job_qdrant_repo = JobQdrantRepository(index_name=cfg.QDRANT_INDEX_JOB_SEARCH)
        self.openai_client = self.ai.openai_client

    # Tool 1: Extract Candidate Profile
    async def extract_candidate_profile(self, resume_text: str) -> dict:
        """Extract skills, level, and major from resume text."""
        try:
            # Reuse existing functions — zero modification
            skills = self.ai.get_skills_and_knowledge_of_resume(resume_text)
            level = self.ai.get_candidate_level(resume_text)
            major = self.ai.get_candidate_major(resume_text)

            return {
                "success": True,
                "skills": skills or [],
                "experience_level": level[0] if level else "Entry level",
                "predicted_major": major[0] if major else "Software Engineer",
                "all_levels": level or [],
                "all_majors": major or [],
            }
        except Exception:
            logger.error(f"extract_candidate_profile failed: {traceback.format_exc()}")
            return {"success": False, "error": "Failed to extract profile", "skills": [], "experience_level": "Unknown"}

    # Tool 2: Search Matching Jobs
    async def search_matching_jobs(self, query: str, top_k: int = 5) -> dict:
        """Search Qdrant for jobs matching a query string."""
        try:
            # Get embedding of query — reuse existing AI embedding function
            query_vector = self.ai.get_embedding(query)
            if query_vector is None:
                return {"success": False, "error": "Failed to embed query", "jobs": []}

            from qdrant_client.http import models
            query_filter = models.Filter(
                must=[
                    models.FieldCondition(key="is_hiring", match=models.MatchValue(value=True))
                ]
            )

            hits = self.job_qdrant_repo.client.search(
                collection_name=self.job_qdrant_repo.index_name,
                query_vector=query_vector.tolist(),
                query_filter=query_filter,
                limit=top_k,
                score_threshold=0.3,
            )

            jobs = []
            for hit in hits:
                p = hit.payload
                jobs.append({
                    "job_id": hit.id,
                    "job_title": p.get("job_title", ""),
                    "common_job_title": p.get("common_job_title", ""),
                    "company_type": p.get("company_type", ""),
                    "hiring_level": p.get("hiring_level", ""),
                    "job_type": p.get("job_type", ""),
                    "work_place": p.get("work_place", ""),
                    "salary_from": p.get("salary_from"),
                    "salary_to": p.get("salary_to"),
                    "city_name": p.get("city_name", ""),
                    "matching_score": round(hit.score, 3),
                    "tags": p.get("job_tags", []),
                })

            return {"success": True, "jobs": jobs, "total_found": len(jobs)}
        except Exception:
            logger.error(f"search_matching_jobs failed: {traceback.format_exc()}")
            return {"success": False, "error": "Job search failed", "jobs": []}

    # Tool 3: Get Market Skill Requirements
    # Searches jobs by target role title and extracts common skill patterns
    async def get_market_skill_requirements(self, target_role: str) -> dict:
        """Get required skills for a target role from real job postings in Qdrant."""
        try:
            # Reuse existing abbreviation function to expand the role query
            expanded_titles = self.ai.get_common_job_title(target_role, """
                ### Given this job title: ### {input} ###
                Return the most common standardized version of this job title.
                Response must be a JSON object: {{"answer": "standardized title"}}
            """)

            # Search jobs with this role title
            query = f"{target_role} requirements skills responsibilities"
            query_vector = self.ai.get_embedding(query)
            if query_vector is None:
                return {"success": False, "requirements": [], "error": "Embedding failed"}

            from qdrant_client.http import models
            hits = self.job_qdrant_repo.client.search(
                collection_name=self.job_qdrant_repo.index_name,
                query_vector=query_vector.tolist(),
                query_filter=models.Filter(
                    must=[models.FieldCondition(key="is_hiring", match=models.MatchValue(value=True))]
                ),
                limit=10,
                score_threshold=0.35,
            )

            # Aggregate tags from top job matches as proxy for market requirements
            skill_freq: dict = {}
            job_contents = []
            for hit in hits:
                p = hit.payload
                for tag in p.get("job_tags", []):
                    skill_freq[tag] = skill_freq.get(tag, 0) + 1
                if p.get("display_content"):
                    job_contents.append(p["display_content"][:500])

            # Get top skills by frequency
            sorted_skills = sorted(skill_freq.items(), key=lambda x: x[1], reverse=True)
            top_skills = [s for s, _ in sorted_skills[:20]]

            # If we have job content, also extract skills via LLM
            if job_contents:
                combined = "\n---\n".join(job_contents[:3])
                llm_skills = self.ai.get_skills_and_knowledge_of_resume(combined)
                if llm_skills:
                    for s in llm_skills:
                        if s not in top_skills:
                            top_skills.append(s)

            return {
                "success": True,
                "target_role": target_role,
                "required_skills": top_skills[:25],
                "jobs_analyzed": len(hits),
            }
        except Exception:
            logger.error(f"get_market_skill_requirements failed: {traceback.format_exc()}")
            return {"success": False, "requirements": [], "error": "Market research failed"}

    # Tool 4: Calculate Skill Gap
    async def calculate_skill_gap(
        self,
        current_skills: list,
        target_role: str,
        market_requirements: list,
    ) -> dict:
        """LLM-powered skill gap analysis between candidate and market requirements."""
        try:
            prompt = SKILL_GAP_ANALYSIS_PROMPT.format(
                current_skills=json.dumps(current_skills),
                target_role=target_role,
                market_requirements=json.dumps(market_requirements),
            )

            response = self.openai_client.chat.completions.create(
                model=self.ai.completion_model,
                messages=[
                    {"role": "system", "content": "You are a precise career skills analyst. Return only valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                top_p=0.2,
            )

            result = json.loads(response.choices[0].message.content)
            result["success"] = True
            return result
        except Exception:
            logger.error(f"calculate_skill_gap failed: {traceback.format_exc()}")
            return {
                "success": False,
                "missing_skills": [],
                "partial_skills": [],
                "strength_skills": current_skills,
                "gap_severity": "unknown",
                "priority_skills": [],
            }

    # Tool 5: Generate Learning Roadmap
    async def generate_learning_roadmap(
        self,
        current_skills: list,
        experience_level: str,
        target_role: str,
        skill_gaps: list,
    ) -> dict:
        """Generate a structured learning roadmap using LLM."""
        try:
            prompt = ROADMAP_GENERATION_PROMPT.format(
                current_skills=json.dumps(current_skills),
                experience_level=experience_level,
                target_role=target_role,
                skill_gaps=json.dumps(skill_gaps),
            )

            response = self.openai_client.chat.completions.create(
                model=self.ai.completion_model,
                messages=[
                    {"role": "system", "content": "You are a career development expert. Return only valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                top_p=0.3,
            )

            result = json.loads(response.choices[0].message.content)
            result["success"] = True
            return result
        except Exception:
            logger.error(f"generate_learning_roadmap failed: {traceback.format_exc()}")
            return {"success": False, "phases": [], "total_duration_months": 0}

    # Tool 6: Evaluate Recommendation (Self-reflection)
    async def evaluate_recommendation(
        self,
        recommendation_summary: str,
        skill_gaps_count: int = 0,
        roadmap_phases_count: int = 0,
        matching_jobs_count: int = 0,
    ) -> dict:
        """Self-evaluate recommendation quality before returning to user."""
        try:
            prompt = EVALUATION_PROMPT.format(recommendation=recommendation_summary)

            response = self.openai_client.chat.completions.create(
                model=self.ai.completion_model_mini,  # Use mini model for evaluation (cheaper)
                messages=[
                    {"role": "system", "content": "You are a strict quality assessor. Return only valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                top_p=0.1,
            )

            result = json.loads(response.choices[0].message.content)
            # Additional metric-based checks
            if skill_gaps_count == 0:
                result["issues"] = result.get("issues", []) + ["No skill gaps identified"]
                result["score"] = min(result.get("score", 10), 5)
            if roadmap_phases_count == 0:
                result["issues"] = result.get("issues", []) + ["No roadmap generated"]
                result["approved"] = False

            result["success"] = True
            return result
        except Exception:
            logger.error(f"evaluate_recommendation failed: {traceback.format_exc()}")
            return {"success": False, "score": 5, "approved": True, "issues": []}

    # Dispatcher — maps tool_name → method
    async def dispatch(self, tool_name: str, tool_args: dict) -> str:
        """Dispatch a tool call from the agent to the correct method."""
        try:
            if tool_name == "extract_candidate_profile":
                result = await self.extract_candidate_profile(**tool_args)
            elif tool_name == "search_matching_jobs":
                result = await self.search_matching_jobs(**tool_args)
            elif tool_name == "get_market_skill_requirements":
                result = await self.get_market_skill_requirements(**tool_args)
            elif tool_name == "calculate_skill_gap":
                result = await self.calculate_skill_gap(**tool_args)
            elif tool_name == "generate_learning_roadmap":
                result = await self.generate_learning_roadmap(**tool_args)
            elif tool_name == "evaluate_recommendation":
                result = await self.evaluate_recommendation(**tool_args)
            else:
                result = {"error": f"Unknown tool: {tool_name}"}

            return json.dumps(result, ensure_ascii=False)
        except Exception:
            logger.error(f"Tool dispatch failed for {tool_name}: {traceback.format_exc()}")
            return json.dumps({"error": f"Tool execution failed: {tool_name}"})
