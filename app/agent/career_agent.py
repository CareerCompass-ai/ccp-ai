"""
Agent v2 - Career Intelligence Agent (Orchestrator)

ReAct Loop: Reason -> Act (Tool Call) -> Observe (Tool Result) -> Repeat -> Final Answer
"""

import json
import traceback
from datetime import datetime
from typing import Optional

from openai import OpenAI

from app.agent.tools import CAREER_AGENT_TOOLS
from app.agent.executor import ToolExecutor
from app.agent.prompts import CAREER_AGENT_SYSTEM_PROMPT
import constant.ai as ai_constant
from pkg.logging import logger


class CareerAgent:
    """
    Agentic Career Counselor powered by OpenAI Function Calling.
    
    Flow:
        User message
            ↓
        Agent (GPT) reasons and selects tools
            ↓
        ToolExecutor executes the tool
            ↓
        Result fed back to agent
            ↓
        Loop until finish_reason == "stop"
            ↓
        Structured final recommendation
    """

    MAX_ITERATIONS = 10  # Safety limit for the ReAct loop

    def __init__(self):
        self.openai_client = OpenAI(api_key=ai_constant.OPENAI_API_KEY)
        self.executor = ToolExecutor()
        self.model = ai_constant.OPENAI_COMPLETION_MODEL
        from app.repo.redis_repo import RedisRepository
        self.redis = RedisRepository()

    def _notify_stream(self, task_id: Optional[str], event_type: str, data: dict):
        if not task_id:
            return
        try:
            payload = {"event": event_type, "task_id": task_id, "timestamp": datetime.utcnow().isoformat(), **data}
            self.redis.publish(f"agent_stream:{task_id}", json.dumps(payload, ensure_ascii=False))
        except Exception:
            pass

    async def run(
        self,
        user_query: str,
        resume_text: Optional[str] = None,
        candidate_id: Optional[int] = None,
        task_id: Optional[str] = None,
    ) -> dict:
        """
        Main entrypoint. Runs the full agentic loop.
        
        Args:
            user_query: The user's career question or goal
            resume_text: Optional raw resume content for profile extraction
            candidate_id: Optional candidate ID (for logging/tracking)
        
        Returns:
            dict with keys: success, answer, steps, metadata
        """
        start_time = datetime.now()
        steps = []

        # Build initial context
        user_content = user_query
        if resume_text:
            user_content = f"My Resume:\n{resume_text}\n\nMy Question: {user_query}"

        messages = [
            {"role": "system", "content": CAREER_AGENT_SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ]

        logger.info(f"[CareerAgent] Starting for candidate={candidate_id}, query='{user_query[:80]}...'")

        try:
            for iteration in range(self.MAX_ITERATIONS):
                # Reason: Ask LLM what to do next
                response = self.openai_client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=CAREER_AGENT_TOOLS,
                    tool_choice="auto",
                    temperature=0.2,
                )

                choice = response.choices[0]
                messages.append(choice.message)

                # Check if agent is done
                if choice.finish_reason == "stop":
                    logger.info(f"[CareerAgent] Completed in {iteration + 1} iterations")
                    final_answer = choice.message.content

                    # Try to parse as JSON, fallback to string
                    try:
                        parsed_answer = json.loads(final_answer)
                    except (json.JSONDecodeError, TypeError):
                        parsed_answer = {"summary": final_answer}

                    res = {
                        "success": True,
                        "answer": parsed_answer,
                        "steps": steps,
                        "iterations": iteration + 1,
                        "duration_seconds": (datetime.now() - start_time).total_seconds(),
                        "candidate_id": candidate_id,
                    }
                    self._notify_stream(task_id, "complete", {"status": "completed", "result": res})
                    self._notify_stream(task_id, "done", {"status": "done"})
                    return res

                # Act: Execute tool calls
                if choice.finish_reason == "tool_calls" and choice.message.tool_calls:
                    tool_results = []

                    for tool_call in choice.message.tool_calls:
                        tool_name = tool_call.function.name
                        try:
                            tool_args = json.loads(tool_call.function.arguments)
                        except json.JSONDecodeError:
                            tool_args = {}

                        logger.info(f"[CareerAgent] Iter {iteration + 1}: Calling tool '{tool_name}' with args {list(tool_args.keys())}")
                        steps.append({
                            "iteration": iteration + 1,
                            "tool": tool_name,
                            "args_summary": list(tool_args.keys()),
                        })

                        self._notify_stream(task_id, "step", {
                            "step": iteration + 1,
                            "tool": tool_name,
                            "message": f"Executing: {tool_name}",
                        })

                        # Observe: Execute and get result
                        tool_result_str = await self.executor.dispatch(tool_name, tool_args)

                        self._notify_stream(task_id, "step_done", {
                            "step": iteration + 1,
                            "tool": tool_name,
                            "message": f"Completed: {tool_name}",
                        })

                        tool_results.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "content": tool_result_str,
                        })

                    # Feed all tool results back to the agent
                    messages.extend(tool_results)

                else:
                    # Unexpected finish reason
                    logger.warning(f"[CareerAgent] Unexpected finish_reason: {choice.finish_reason}")
                    break

            # Max iterations reached
            logger.warning(f"[CareerAgent] Max iterations ({self.MAX_ITERATIONS}) reached")
            return {
                "success": False,
                "error": "Agent reached maximum iterations without completing",
                "steps": steps,
                "iterations": self.MAX_ITERATIONS,
                "duration_seconds": (datetime.now() - start_time).total_seconds(),
            }

        except Exception:
            logger.error(f"[CareerAgent] Fatal error: {traceback.format_exc()}")
            return {
                "success": False,
                "error": "Agent encountered an internal error",
                "steps": steps,
                "duration_seconds": (datetime.now() - start_time).total_seconds(),
            }
