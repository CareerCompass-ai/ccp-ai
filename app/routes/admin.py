from fastapi import APIRouter, FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from constant import config

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


@admin_router.post("/weaviate/create-class-name")
async def create_weaviate_schema():
    pass