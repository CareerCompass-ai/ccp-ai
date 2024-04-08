from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes.job_routes import job_router
from .routes.resume_routes import resume_router
from .routes.common_routes import common_router
from .routes.candidate_routes import candidate_router

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(job_router)
app.include_router(resume_router)
app.include_router(candidate_router)
# common router
app.include_router(common_router)

@app.get("/health-check")
async def root():
    return {"message": "Good"}
