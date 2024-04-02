import constant.config as constant

from typing import List, Optional
from minio import Minio
from app.dto import job
import os
import PyPDF2
from io import BytesIO
class JobMinioRepository:
    def __init__(self):
        self.client = Minio (
            endpoint= constant.MINIO_URL,
            access_key=constant.MINIO_USERNAME,
            secret_key=constant.MINIO_PASSWORD,
            secure=False
        )
    def upload_job_to_minio(self, input: Optional[job.UploadJobMinioRequest]) -> job.UploadJobMinioResponse:
        if self.client.bucket_exists(constant.MINIO_BUCKET_JOB):
            self.client.fput_object(constant.MINIO_BUCKET_JOB, input.file_name, input.temp_path)
            return job.UploadJobMinioResponse(
                url=constant.MINIO_BUCKET_JOB+"/" + input.file_name
            )
        else:
            print("Bucket does not exist")
