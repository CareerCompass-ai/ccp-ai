import constant.config as constant

from typing import List, Optional
from minio import Minio
from app.dto import resume

class ResumeMinioRepository:
    def __init__(self):
        self.client = Minio (
            endpoint= constant.MINIO_URL,
            access_key=constant.MINIO_USERNAME,
            secret_key=constant.MINIO_PASSWORD,
            secure=False
        )
    
    def upload_resume_to_minio(self, input: Optional[resume.ResumeurlRequest]) -> resume.ResumeResponse_Url:
        if self.client.bucket_exists("ccp"):
            result = self.client.fput_object("ccp", input.resume_name, input.resume_path)
            print("Resume uploaded: ", result)
            return resume.ResumeResponse_Url(
                resume_name=input.resume_name,
                bucket_name="ccp",
                minio_resume_link="ccp/" + input.resume_name 
            )
        else:
            print("Bucket does not exist")