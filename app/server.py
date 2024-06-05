from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes.admin import admin_router
from .routes.ai_router import ai_router
from .routes.analysis_routes import analysis_router
from .routes.candidate_routes import candidate_router
from .routes.common_routes import common_router
from .routes.job_routes import job_router
from .routes.recruiter_routes import recruiter_router
from .routes.resume_routes import resume_router

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# admin router, for fixing and configurating stuffs
app.include_router(admin_router)

app.include_router(job_router)
app.include_router(resume_router)
app.include_router(candidate_router)
app.include_router(recruiter_router)
app.include_router(analysis_router)

# common router
app.include_router(common_router)

# AI router
app.include_router(ai_router)

@app.get("/health-check")
async def root():
    return {"message": "Good"}
