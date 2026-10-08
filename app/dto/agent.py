"""
Agent v2 - DTOs for /api/v2/agent/* endpoints

Tách biệt hoàn toàn khỏi DTOs cũ để không đụng vào flow hiện tại.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel


# ─── Request Models ───────────────────────────────────────────────────────────

class AgentCareerRequest(BaseModel):
    """
    Request to run the full agentic career recommendation.
    
    Modes:
    1. resume_text + query → Full analysis from raw text
    2. candidate_id + query → Load resume from DB automatically
    3. query only → General career advice (no personal analysis)
    """
    query: str
    resume_text: Optional[str] = None
    candidate_id: Optional[int] = None
    stream: bool = False  # Future: SSE streaming support


class AgentStatusRequest(BaseModel):
    """Poll async task status (when running via background worker)."""
    task_id: str


# ─── Response Models ──────────────────────────────────────────────────────────

class AgentStep(BaseModel):
    """One iteration step in the agent's ReAct loop."""
    iteration: int
    tool: str
    args_summary: List[str]


class SkillGap(BaseModel):
    skill: str
    current_level: Optional[str] = None
    required_level: Optional[str] = None


class RoadmapResource(BaseModel):
    type: str  # course | book | project
    title: str
    url: Optional[str] = None
    priority: str  # high | medium | low


class RoadmapPhase(BaseModel):
    phase: int
    title: str
    duration_weeks: int
    goals: List[str]
    resources: List[RoadmapResource]
    milestone: str


class MatchingJob(BaseModel):
    job_id: int
    job_title: str
    common_job_title: Optional[str] = None
    company_type: Optional[str] = None
    hiring_level: Optional[str] = None
    job_type: Optional[str] = None
    work_place: Optional[str] = None
    salary_from: Optional[float] = None
    salary_to: Optional[float] = None
    city_name: Optional[str] = None
    matching_score: float
    tags: List[str] = []


class CareerRecommendation(BaseModel):
    summary: str
    current_level: Optional[str] = None
    current_skills: List[str] = []
    target_role: Optional[str] = None
    matching_jobs: List[MatchingJob] = []
    skill_gaps: List[str] = []
    partial_skills: List[SkillGap] = []
    strength_skills: List[str] = []
    gap_severity: Optional[str] = None
    roadmap: Optional[List[RoadmapPhase]] = None
    estimated_time: Optional[str] = None
    key_projects: List[str] = []
    certifications: List[str] = []
    evaluation_score: Optional[float] = None


class AgentCareerResponse(BaseModel):
    success: bool
    task_mode: str  # "sync" | "async"
    answer: Optional[CareerRecommendation] = None
    raw_answer: Optional[Dict[str, Any]] = None  # Fallback if parsing fails
    steps: List[AgentStep] = []
    iterations: Optional[int] = None
    duration_seconds: Optional[float] = None
    error: Optional[str] = None
    task_id: Optional[str] = None  # Set when running async via background


class AgentStatusResponse(BaseModel):
    task_id: str
    status: str  # pending | running | completed | failed
    result: Optional[AgentCareerResponse] = None
    created_at: Optional[str] = None
    completed_at: Optional[str] = None


class AgentHistoryItemResponse(BaseModel):
    id: int
    task_id: str
    candidate_id: Optional[int] = None
    query: str
    summary: Optional[str] = None
    target_role: Optional[str] = None
    evaluation_score: Optional[float] = None
    duration_seconds: Optional[float] = None
    created_at: Optional[str] = None
    completed_at: Optional[str] = None


class AgentHistoryDetailResponse(BaseModel):
    id: int
    task_id: str
    candidate_id: Optional[int] = None
    query: str
    summary: Optional[str] = None
    target_role: Optional[str] = None
    matching_jobs: Optional[Any] = None
    skill_gaps: Optional[Any] = None
    roadmap: Optional[Any] = None
    evaluation_score: Optional[float] = None
    result: Optional[AgentCareerResponse] = None
    steps: Optional[Any] = None
    duration_seconds: Optional[float] = None
    created_at: Optional[str] = None
    completed_at: Optional[str] = None

