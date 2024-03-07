from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import func

from config import postgres
from models import ccp_job
from app.dto import job

job_router = APIRouter(
    prefix="/job",
    tags=['Job']
)

@job_router.get("/list", response_model=List[job.JobBase])
def get_jobs(db: Session = Depends(postgres.init_db)):
    jobs = db.query(ccp_job.Job).all()
    return [job.JobBase(**j.__dict__) for j in jobs]

@job_router.get("/ping")
async def root():
    return {"message": "pong"}