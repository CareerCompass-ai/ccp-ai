import constant.config as constant

from typing import List, Optional
from minio import Minio
from minio.error import S3Error

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
                url=input.file_name
            )
        else:
            print("Bucket does not exist")

    def generate_presigned_url(self, object_name: str) -> str:
        try:
            return self.client.presigned_put_object(constant.MINIO_BUCKET_JOB, object_name)
        except S3Error as err:
            print(f"Error generating pre-signed URL: {err}")

    def remove_job_from_minio(self, file_name):
        if self.client.bucket_exists(constant.MINIO_BUCKET_JOB):
            self.client.remove_object(constant.MINIO_BUCKET_JOB, str(file_name))
        else:
            print("Bucket does not exist")
