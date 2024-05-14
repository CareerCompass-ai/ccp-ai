import constant.config as constant

from typing import List, Optional
from minio import Minio
from minio.error import S3Error
from app.dto import resume

import PyPDF2
from io import BytesIO
class ResumeMinioRepository:
    def __init__(self):
        self.client = Minio (
            endpoint= constant.MINIO_URL,
            access_key=constant.MINIO_USERNAME,
            secret_key=constant.MINIO_PASSWORD,
            secure=False
        )
    
    def upload_resume_to_minio(self, input: Optional[resume.UploadResumeMinioRequest]) -> resume.UploadResumeMinioResponse:
        if self.client.bucket_exists(constant.MINIO_BUCKET_RESUME):
            self.client.fput_object(constant.MINIO_BUCKET_RESUME, input.file_name, input.temp_path)
            return resume.UploadResumeMinioResponse(
                url=input.file_name
            )
        else:
            print("Bucket does not exist")

    def generate_presigned_url(self, object_name: str) -> str:
        try:
            return self.client.presigned_put_object(constant.MINIO_BUCKET_RESUME, object_name)
        except S3Error as err:
            print(f"Error generating pre-signed URL: {err}")