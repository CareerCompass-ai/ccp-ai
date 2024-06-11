from datetime import datetime
from typing import Optional

from fastapi import (APIRouter, Depends, File, Form, HTTPException, Path,
                     Query, UploadFile, status)
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

import constant.ai as constant
import constant.config as minio_constant
from app.factory.factory import RepositoryFactory as factory
from config import postgres
from config.postgres import PostgresDB
from constant import config as cfg
from pkg.logging import logger


class NotificationsRouter:
    def __init__(self):
        self.notifications_repo = factory.get_notifications_repo()

        self.router = APIRouter(prefix="/api", tags=['Notifications'])
        # self.router.add_api_route("/jobs", self.list_jobs_from_qdrant, methods=["GET"], response_model=job.ListJobResponse)
        
    # async def list_notifications(self, request):
    #     try:
    #         # Get all notifications
    #         notifications = await self.notification_repo.get_all()
    #         return notifications
    #     except Exception as e:
    #         logger.error(f"Error in listing notifications: {e}")
    #         return []
        
    # async def update_read_notifications(self, request):
    #     try:
    #         # Get all notifications
    #         notifications = await self.notification_repo.get_all()
    #         return notifications
    #     except Exception as e:
    #         logger.error(f"Error in listing notifications: {e}")
    #         return []
        
notifications_router = NotificationsRouter().router