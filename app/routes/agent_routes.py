"""
Agent v2 - FastAPI Routes

Prefix: /api/v2/agent/

Endpoints:
  POST /api/v2/agent/career          → Sync: Run agent, wait for result
  POST /api/v2/agent/career/async    → Async: Submit task to background via Kafka
  GET  /api/v2/agent/status/{task_id} → Poll async task result

Design:
- KHÔNG đụng vào router cũ
- Frontend switch từ endpoint cũ sang /api/v2/agent/ khi sẵn sàng
- Auth sử dụng JWTMiddleware hiện tại (không cần thay đổi)
"""

import asyncio
import json
import time
import traceback
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.agent.career_agent import CareerAgent
from app.dto.agent import (
    AgentCareerRequest,
    AgentCareerResponse,
    AgentStatusResponse,
    AgentHistoryItemResponse,
    AgentHistoryDetailResponse,
    CareerRecommendation,
    AgentStep,
    MatchingJob,
    SkillGap,
    RoadmapPhase,
    RoadmapResource,
)
from app.factory.factory import RepositoryFactory as factory
from app.repo.redis_repo import RedisRepository
from app.repo.agent_history_repo import AgentHistoryRepository
from config.postgres import PostgresDB
from pkg.logging import logger

agent_router = APIRouter(
    prefix="/api/v2/agent",
    tags=["Agent v2"]
)

# Redis-backed task store — survives restarts, works across multiple instances
# Key pattern: agent_task:{task_id}
# TTL: 24 hours (tasks auto-expire)
_TASK_KEY_PREFIX = "agent_task"
_TASK_TTL_SECONDS = 86400  # 24h
_redis = RedisRepository()


def _task_key(task_id: str) -> str:
    return f"{_TASK_KEY_PREFIX}:{task_id}"


def _write_task(task_id: str, data: dict):
    """Write task state to Redis with 24h TTL."""
    try:
        _redis.set(_task_key(task_id), json.dumps(data, ensure_ascii=False), expire=_TASK_TTL_SECONDS)
    except Exception:
        logger.error(f"[AgentRoute] Failed to write task {task_id} to Redis: {traceback.format_exc()}")


def _read_task(task_id: str) -> Optional[dict]:
    """Read task state from Redis."""
    try:
        raw = _redis.get(_task_key(task_id))
        if raw:
            return json.loads(raw)
        return None
    except Exception:
        logger.error(f"[AgentRoute] Failed to read task {task_id} from Redis: {traceback.format_exc()}")
        return None

# ─── Helpers ──────────────────────────────────────────────────────────────────

def _parse_agent_answer(raw_answer: dict) -> Optional[CareerRecommendation]:
    """Safely parse the raw agent JSON output into CareerRecommendation DTO."""
    try:
        # Parse matching jobs
        matching_jobs = []
        for j in raw_answer.get("matching_jobs", []):
            try:
                matching_jobs.append(MatchingJob(**j))
            except Exception:
                pass

        # Parse skill gaps (handle both list[str] and list[dict])
        skill_gaps_raw = raw_answer.get("skill_gaps", [])
        skill_gaps = []
        for sg in skill_gaps_raw:
            if isinstance(sg, str):
                skill_gaps.append(sg)
            elif isinstance(sg, dict):
                skill_gaps.append(sg.get("skill", str(sg)))

        # Parse partial skills
        partial_skills = []
        for ps in raw_answer.get("partial_skills", []):
            try:
                partial_skills.append(SkillGap(**ps))
            except Exception:
                pass

        # Parse roadmap phases
        roadmap_phases = None
        phases_raw = raw_answer.get("roadmap", raw_answer.get("phases"))
        if phases_raw and isinstance(phases_raw, list):
            roadmap_phases = []
            for ph in phases_raw:
                try:
                    resources = [RoadmapResource(**r) for r in ph.get("resources", [])]
                    roadmap_phases.append(RoadmapPhase(
                        phase=ph.get("phase", 0),
                        title=ph.get("title", ""),
                        duration_weeks=ph.get("duration_weeks", 0),
                        goals=ph.get("goals", []),
                        resources=resources,
                        milestone=ph.get("milestone", ""),
                    ))
                except Exception:
                    pass

        return CareerRecommendation(
            summary=raw_answer.get("summary", ""),
            current_level=raw_answer.get("current_level"),
            current_skills=raw_answer.get("current_skills", []),
            target_role=raw_answer.get("target_role"),
            matching_jobs=matching_jobs,
            skill_gaps=skill_gaps,
            partial_skills=partial_skills,
            strength_skills=raw_answer.get("strength_skills", []),
            gap_severity=raw_answer.get("gap_severity"),
            roadmap=roadmap_phases,
            estimated_time=raw_answer.get("estimated_time"),
            key_projects=raw_answer.get("key_projects", []),
            certifications=raw_answer.get("certifications", []),
            evaluation_score=raw_answer.get("evaluation_score"),
        )
    except Exception:
        logger.error(f"Failed to parse agent answer: {traceback.format_exc()}")
        return None


# ─── Endpoints ────────────────────────────────────────────────────────────────

@agent_router.post(
    "/career",
    response_model=AgentCareerResponse,
    summary="[v2] Run Career Intelligence Agent (Sync)",
    description="""
    Run the full agentic career analysis pipeline synchronously.
    
    The agent will:
    1. Extract your profile from resume text
    2. Search matching jobs in the database
    3. Identify market requirements for your target role
    4. Calculate skill gaps
    5. Generate a learning roadmap
    6. Self-evaluate the recommendation
    
    NOTE: This endpoint can take 15-45 seconds for a full analysis.
    For long-running analysis, use POST /career/async instead.
    """
)
async def run_career_agent_sync(
    req: AgentCareerRequest,
    db: Session = Depends(PostgresDB.get_db),
):
    """
    Synchronous agent endpoint.
    Loads resume from DB if candidate_id is provided but resume_text is not.
    """
    resume_text = req.resume_text

    # Auto-load resume from DB if candidate_id given without text
    if not resume_text and req.candidate_id:
        try:
            resume_repo = factory.get_resume_repo()
            resumes = await resume_repo.get_by_user_id(db=db, user_id=req.candidate_id)
            if resumes:
                # Use most recent resume
                latest = max(resumes, key=lambda r: r.updated_at)
                resume_text = latest.content or ""
                logger.info(f"[AgentRoute] Loaded resume {latest.id} for candidate {req.candidate_id}")
        except Exception:
            logger.warning(f"[AgentRoute] Failed to load resume from DB: {traceback.format_exc()}")

    # Run agent
    agent = CareerAgent()
    result = await agent.run(
        user_query=req.query,
        resume_text=resume_text,
        candidate_id=req.candidate_id,
    )

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "Agent failed to complete")
        )

    # Parse structured answer
    raw_answer = result.get("answer", {})
    parsed = _parse_agent_answer(raw_answer)

    steps = [AgentStep(**s) for s in result.get("steps", [])]
    task_id = str(uuid.uuid4())

    # Save to PostgreSQL history if candidate_id is present
    if req.candidate_id:
        try:
            repo = AgentHistoryRepository()
            repo.save(db, {
                "task_id": task_id,
                "candidate_id": req.candidate_id,
                "query": req.query,
                "status": "completed",
                "summary": raw_answer.get("summary") if isinstance(raw_answer, dict) else str(raw_answer),
                "target_role": raw_answer.get("target_role") if isinstance(raw_answer, dict) else None,
                "matching_jobs": raw_answer.get("matching_jobs") if isinstance(raw_answer, dict) else None,
                "skill_gaps": raw_answer.get("skill_gaps") if isinstance(raw_answer, dict) else None,
                "roadmap": raw_answer.get("roadmap") if isinstance(raw_answer, dict) else None,
                "evaluation_score": raw_answer.get("evaluation_score") if isinstance(raw_answer, dict) else None,
                "result_json": result,
                "steps": result.get("steps", []),
                "iterations": result.get("iterations"),
                "duration_seconds": result.get("duration_seconds"),
                "completed_at": datetime.utcnow(),
            })
        except Exception:
            logger.warning(f"[AgentRoute] Failed to save sync run to history: {traceback.format_exc()}")

    return AgentCareerResponse(
        success=True,
        task_mode="sync",
        task_id=task_id,
        answer=parsed,
        raw_answer=raw_answer if parsed is None else None,
        steps=steps,
        iterations=result.get("iterations"),
        duration_seconds=result.get("duration_seconds"),
    )


@agent_router.post(
    "/career/async",
    response_model=AgentCareerResponse,
    summary="[v2] Submit Career Agent Task (Async via Kafka)",
    description="""
    Submit the career analysis task to the background worker via Kafka.
    Returns immediately with a task_id.
    Poll GET /status/{task_id} to get the result when ready.
    
    Recommended for production use — does not block the HTTP connection.
    """
)
async def run_career_agent_async(
    req: AgentCareerRequest,
    db: Session = Depends(PostgresDB.get_db),
):
    """
    Async agent endpoint: produces to Kafka topic ccp_agent_task.
    Background worker (ccp-background) consumes and runs the agent.
    """
    task_id = str(uuid.uuid4())

    # Resolve resume text if needed
    resume_text = req.resume_text
    if not resume_text and req.candidate_id:
        try:
            resume_repo = factory.get_resume_repo()
            resumes = await resume_repo.get_by_user_id(db=db, user_id=req.candidate_id)
            if resumes:
                latest = max(resumes, key=lambda r: r.updated_at)
                resume_text = latest.content or ""
        except Exception:
            logger.warning(f"[AgentRoute] Could not load resume: {traceback.format_exc()}")

    # Produce to Kafka
    try:
        kafka_producer = factory.get_kafka_producer()
        payload = {
            "task_id": task_id,
            "query": req.query,
            "resume_text": resume_text or "",
            "candidate_id": req.candidate_id,
            "created_at": datetime.utcnow().isoformat(),
        }
        kafka_producer.produce(
            topic="ccp_agent_task",
            value=json.dumps(payload, ensure_ascii=False),
        )
        logger.info(f"[AgentRoute] Task {task_id} sent to Kafka for candidate={req.candidate_id}")
    except Exception:
        logger.error(f"[AgentRoute] Kafka produce failed: {traceback.format_exc()}")
        # Fallback: run synchronously if Kafka fails
        logger.info(f"[AgentRoute] Falling back to sync for task {task_id}")
        agent = CareerAgent()
        result = await agent.run(req.query, resume_text, req.candidate_id)
        raw_answer = result.get("answer", {})
        parsed = _parse_agent_answer(raw_answer)
        steps = [AgentStep(**s) for s in result.get("steps", [])]
        return AgentCareerResponse(
            success=result["success"],
            task_mode="sync_fallback",
            task_id=task_id,
            answer=parsed,
            steps=steps,
            iterations=result.get("iterations"),
            duration_seconds=result.get("duration_seconds"),
            error=result.get("error"),
        )

    # Write initial pending state to Redis so FE can see it immediately
    _write_task(task_id, {
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
    })

    return AgentCareerResponse(
        success=True,
        task_mode="async",
        task_id=task_id,
        answer=None,
    )


@agent_router.get(
    "/status/{task_id}",
    response_model=AgentStatusResponse,
    summary="[v2] Poll Async Agent Task Status",
)
async def get_agent_task_status(task_id: str):
    """
    Poll the status of an async agent task.
    The background worker (ccp-background) writes results here when done.
    
    Status: pending → running → completed | failed
    """
    stored = _read_task(task_id)
    if not stored:
        return AgentStatusResponse(
            task_id=task_id,
            status="pending",
            result=None,
        )

    # Deserialize result if present
    result_data = stored.get("result")
    parsed_result = None
    if result_data:
        try:
            parsed_result = AgentCareerResponse(**result_data)
        except Exception:
            logger.warning(f"[AgentRoute] Could not deserialize result for {task_id}")

    return AgentStatusResponse(
        task_id=task_id,
        status=stored.get("status", "pending"),
        result=parsed_result,
        created_at=stored.get("created_at"),
        completed_at=stored.get("completed_at"),
    )


@agent_router.post(
    "/status/{task_id}/complete",
    include_in_schema=False,  # Internal endpoint for background worker
    summary="[Internal] Background worker writes task result",
)
async def complete_agent_task(task_id: str, result: AgentCareerResponse, db: Session = Depends(PostgresDB.get_db)):
    """
    Called by background worker when agent task completes.
    Internal endpoint — writes to Redis, notifies SSE stream, and persists history.
    """
    result_dict = result.model_dump()
    _write_task(task_id, {
        "status": "completed" if result.success else "failed",
        "result": result_dict,
        "completed_at": datetime.utcnow().isoformat(),
    })

    # Also notify SSE stream if anyone is listening
    try:
        _redis.publish(
            f"agent_stream:{task_id}",
            json.dumps({
                "event": "complete" if result.success else "failed",
                "task_id": task_id,
                "status": "completed" if result.success else "failed",
                "result": result_dict,
            }, ensure_ascii=False)
        )
    except Exception:
        pass

    logger.info(f"[AgentRoute] Task {task_id} written to Redis. Success={result.success}")
    return {"message": "Task result stored"}


@agent_router.get(
    "/stream/{task_id}",
    summary="[v2] Real-time SSE Stream of Agent Progress & Result",
    description="""
    Connect via Server-Sent Events (SSE) to receive real-time step-by-step updates
    and the final recommendation as it executes in the background worker.

    Frontend usage:
      const es = new EventSource('/api/v2/agent/stream/' + taskId);
      es.addEventListener('status', (e) => console.log('Status:', JSON.parse(e.data)));
      es.addEventListener('step', (e) => console.log('Step:', JSON.parse(e.data)));
      es.addEventListener('complete', (e) => {
        const data = JSON.parse(e.data);
        // Render final career roadmap!
        es.close();
      });
    """
)
async def stream_agent_task(task_id: str, last_seq: int = 0):
    """
    Server-Sent Events (SSE) streaming endpoint:
    1. Replays past events from Redis list 'agent_events:{task_id}' (prevents race conditions)
    2. Subscribes to Redis Pub/Sub channel 'agent_stream:{task_id}' for live events
    3. Guarantees zero missed events even if Frontend connects late or reconnects.
    """
    async def event_generator():
        current_seq = last_seq

        # 1. REPLAY PAST EVENTS from Redis List
        events_key = f"agent_events:{task_id}"
        past_events = _redis.lrange(events_key, 0, -1)
        already_finished = False

        for raw_event in past_events:
            try:
                event_obj = json.loads(raw_event)
                seq = event_obj.get("seq", 0)
                event_name = event_obj.get("event", "message")

                if seq > current_seq:
                    yield f"event: {event_name}\ndata: {raw_event}\n\n"
                    current_seq = seq

                if event_name in ["complete", "failed", "done"]:
                    already_finished = True
            except Exception:
                pass

        # If task already completed during replay, exit cleanly
        if already_finished:
            return

        # Fast path check in case events list was empty but task finished
        cached = _read_task(task_id)
        if cached and cached.get("status") in ["completed", "failed"]:
            st = cached.get("status")
            yield f"event: {st}\ndata: {json.dumps(cached, ensure_ascii=False)}\n\n"
            yield f"event: done\ndata: {json.dumps({'status': 'done'})}\n\n"
            return

        # 2. SUBSCRIBE TO LIVE EVENTS
        pubsub = _redis.get_pubsub()
        if not pubsub:
            yield f"event: error\ndata: {json.dumps({'error': 'Redis pubsub unavailable'})}\n\n"
            return

        channel = f"agent_stream:{task_id}"
        pubsub.subscribe(channel)

        timeout_seconds = 180  # 3 mins max connection duration
        start_time = time.time()

        try:
            while time.time() - start_time < timeout_seconds:
                message = pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message and message.get("data"):
                    raw_data = message["data"]
                    data_str = raw_data.decode("utf-8") if isinstance(raw_data, bytes) else raw_data
                    try:
                        event_obj = json.loads(data_str)
                        event_name = event_obj.get("event", "message")
                        seq = event_obj.get("seq", current_seq + 1)
                    except Exception:
                        event_name = "message"
                        seq = current_seq + 1

                    # Only yield if seq is greater than what was already replayed
                    if seq > current_seq:
                        yield f"event: {event_name}\ndata: {data_str}\n\n"
                        current_seq = seq

                    if event_name in ["complete", "failed", "done"]:
                        break
                else:
                    # SSE keep-alive comment
                    yield ": keep-alive\n\n"
                    await asyncio.sleep(0.5)

                    # Also verify Redis state in case complete event was missed
                    current = _read_task(task_id)
                    if current and current.get("status") in ["completed", "failed"]:
                        final_st = current.get("status")
                        yield f"event: {final_st}\ndata: {json.dumps(current, ensure_ascii=False)}\n\n"
                        yield f"event: done\ndata: {json.dumps({'status': 'done'})}\n\n"
                        break
        finally:
            try:
                pubsub.unsubscribe(channel)
                pubsub.close()
            except Exception:
                pass

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@agent_router.get(
    "/history",
    response_model=List[AgentHistoryItemResponse],
    summary="[v2] Get Career Consultation History for Candidate",
    description="Retrieve all past career agent consultations saved in PostgreSQL for a candidate."
)
async def get_career_history(
    candidate_id: int,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(PostgresDB.get_db),
):
    repo = AgentHistoryRepository()
    records = repo.list_by_candidate(db=db, candidate_id=candidate_id, limit=limit, offset=offset)
    return [
        AgentHistoryItemResponse(
            id=r.id,
            task_id=r.task_id,
            candidate_id=r.candidate_id,
            query=r.query or "",
            summary=r.summary,
            target_role=r.target_role,
            evaluation_score=r.evaluation_score,
            duration_seconds=r.duration_seconds,
            created_at=r.created_at.isoformat() if r.created_at else None,
            completed_at=r.completed_at.isoformat() if r.completed_at else None,
        )
        for r in records
    ]


@agent_router.get(
    "/history/{task_id}",
    response_model=AgentHistoryDetailResponse,
    summary="[v2] Get Detailed Past Career Consultation by Task ID",
    description="Retrieve the complete saved recommendation, roadmap, skill gaps, and jobs for a specific past consultation."
)
async def get_career_history_detail(
    task_id: str,
    db: Session = Depends(PostgresDB.get_db),
):
    repo = AgentHistoryRepository()
    record = repo.get_by_task_id(db=db, task_id=task_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Consultation history with task_id {task_id} not found",
        )

    parsed_result = None
    if record.result_json:
        try:
            parsed_result = AgentCareerResponse(**record.result_json)
        except Exception:
            pass

    return AgentHistoryDetailResponse(
        id=record.id,
        task_id=record.task_id,
        candidate_id=record.candidate_id,
        query=record.query or "",
        summary=record.summary,
        target_role=record.target_role,
        matching_jobs=record.matching_jobs,
        skill_gaps=record.skill_gaps,
        roadmap=record.roadmap,
        evaluation_score=record.evaluation_score,
        result=parsed_result,
        steps=record.steps,
        duration_seconds=record.duration_seconds,
        created_at=record.created_at.isoformat() if record.created_at else None,
        completed_at=record.completed_at.isoformat() if record.completed_at else None,
    )

