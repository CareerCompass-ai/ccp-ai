from fastapi import APIRouter, FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from constant import config
from ..dto.admin import DeleteClassRequest

from config.weaviate import WeaviateVDB as weaviate


admin_router = APIRouter(
    prefix="/admin/api",
    tags=['Admin']
)

security = HTTPBasic()

def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = config.HTTP_ADMIN_USER_NAME
    correct_password = config.HTTP_ADMIN_PASSWORD
    if credentials.username != correct_username or credentials.password != correct_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong way",
            headers={"WWW-Authenticate": "Basic"},
        )
    return True

@admin_router.get("/protected")
async def protected_route(is_authenticated: bool = Depends(authenticate_user)):
    return {"message": "You are authorized to access this resource"}


@admin_router.post("/weaviate/create-job-class")
async def create_job_class(is_authenticated: bool = Depends(authenticate_user)):
    client = weaviate.setup_weaviate_connection()

    try:
        # client.schema.create_from_config(weaviate.jobClass)
        # client.collections.create(
        #     "Job",
        #     "Job collection",
        # )
        client.collections.create_from_dict(weaviate.jobClass)
        return {"message": "Job class created successfully"}
    except Exception as e:
        return {"error": str(e)}
    
@admin_router.post("/weaviate/create-jobqna-class")
async def create_job_class(is_authenticated: bool = Depends(authenticate_user)):
    client = weaviate.setup_weaviate_connection()

    try:
        client.collections.create_from_dict(weaviate.jobQnAClass)
        return {"message": "JobQnA class created successfully"}
    except Exception as e:
        return {"error": str(e)}
    
@admin_router.delete("/weaviate/class")
async def delete_class(payload: DeleteClassRequest, is_authenticated: bool = Depends(authenticate_user)):
    client = weaviate.setup_weaviate_connection()

    try:
        client.collections.delete(payload.collection_name)
        return {"message": "JobQnA class created successfully"}
    except Exception as e:
        return {"error": str(e)}