import constant.config as constant

from typing import List, Optional
from minio import Minio
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
        if self.client.bucket_exists("ccp"):
            self.client.fput_object("ccp", input.file_name, input.temp_path)
            return resume.UploadResumeMinioResponse(
                url="ccp/" + input.file_name
            )
        else:
            print("Bucket does not exist")