"""
Agent v2 - Tool Definitions for Career Intelligence Agent

OpenAI Function Calling schema: https://platform.openai.com/docs/guides/function-calling
"""

CAREER_AGENT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "extract_candidate_profile",
            "description": "Extract structured profile from a candidate's resume text. Returns skills, experience level, and predicted major/role.",
            "parameters": {
                "type": "object",
                "properties": {
                    "resume_text": {
                        "type": "string",
                        "description": "The full text content of the candidate's resume."
                    }
                },
                "required": ["resume_text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_matching_jobs",
            "description": "Search for relevant job openings from Qdrant vector DB based on a natural language query about skills or role. Returns top matching jobs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language query for job search, e.g. 'Python backend engineer with microservices experience'"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of jobs to return. Default is 5.",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_market_skill_requirements",
            "description": "Get the commonly required skills and keywords for a target job role from the market (Qdrant job database). Useful for understanding what skills a specific role needs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "target_role": {
                        "type": "string",
                        "description": "The job role to get market requirements for, e.g. 'Machine Learning Engineer', 'DevOps Engineer'"
                    }
                },
                "required": ["target_role"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_skill_gap",
            "description": "Analyze the gap between a candidate's current skills and what is required for a target role. Returns missing skills, partial skills, and priority learning areas.",
            "parameters": {
                "type": "object",
                "properties": {
                    "current_skills": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of skills the candidate currently has."
                    },
                    "target_role": {
                        "type": "string",
                        "description": "The role the candidate wants to transition into."
                    },
                    "market_requirements": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of skills commonly required by market for the target role."
                    }
                },
                "required": ["current_skills", "target_role", "market_requirements"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_learning_roadmap",
            "description": "Generate a structured, phased learning roadmap to help a candidate acquire missing skills and transition to their target role.",
            "parameters": {
                "type": "object",
                "properties": {
                    "current_skills": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Candidate's current skills."
                    },
                    "experience_level": {
                        "type": "string",
                        "description": "Candidate's current level: Entry level, Junior level, Mid-Senior level, etc."
                    },
                    "target_role": {
                        "type": "string",
                        "description": "The target career role."
                    },
                    "skill_gaps": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of skills to acquire."
                    }
                },
                "required": ["current_skills", "experience_level", "target_role", "skill_gaps"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "evaluate_recommendation",
            "description": "Self-evaluate the quality and completeness of the career recommendation before returning to the user. Returns a score and approval status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "recommendation_summary": {
                        "type": "string",
                        "description": "The full recommendation text/summary to evaluate."
                    },
                    "skill_gaps_count": {
                        "type": "integer",
                        "description": "Number of skill gaps identified."
                    },
                    "roadmap_phases_count": {
                        "type": "integer",
                        "description": "Number of phases in the generated roadmap."
                    },
                    "matching_jobs_count": {
                        "type": "integer",
                        "description": "Number of matching jobs found."
                    }
                },
                "required": ["recommendation_summary"]
            }
        }
    }
]
