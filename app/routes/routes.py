from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional

from sqlalchemy import func
from ...config.database import init_db
from ...models import ccp_job


router = APIRouter(
    prefix="/job",
    tags=['Job']
)

@router.get("/jobs", response_model=List[ccp_job.Job])
def get_posts():
    pass