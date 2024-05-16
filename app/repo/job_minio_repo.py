import traceback
import constant.config as constant

from typing import Optional
from minio import Minio
from minio.error import S3Error

from app.dto import job

from pkg.logging import logger

class JobMinioRepository:
    def __init__(self):
        self.client = Minio (
            endpoint= constant.MINIO_URL,
            access_key=constant.MINIO_USERNAME,
            secret_key=constant.MINIO_PASSWORD,
            secure=False
        )

    def upload_job_to_minio(self, input: Optional[job.UploadJobMinioRequest]) -> job.UploadJobMinioResponse:
        try:
            if not self.client.bucket_exists(constant.MINIO_BUCKET_JOB):
                self.client.make_bucket(constant.MINIO_BUCKET_JOB)
                logger.info(f"Bucket {constant.MINIO_BUCKET_JOB} created")

            self.client.fput_object(
                constant.MINIO_BUCKET_JOB,
                input.file_name,
                input.temp_path
            )

            return job.UploadJobMinioResponse(
                url=f"{constant.MINIO_URL}/{constant.MINIO_BUCKET_JOB}/{input.file_name}"
            )

        except S3Error as e:
            logger.error(f"upload_job_to_minio: Failed to upload file to MinIO: {traceback.format_exc()}")
            raise


    def generate_presigned_url(self, object_name: str) -> str:
        try:
            return self.client.presigned_put_object(constant.MINIO_BUCKET_JOB, object_name)
        except S3Error as err:
            logger.error(f"generate_presigned_url: Error generating pre-signed URL: {traceback.format_exc()}")

    def remove_job_from_minio(self, file_name):
        if self.client.bucket_exists(constant.MINIO_BUCKET_JOB):
            self.client.remove_object(constant.MINIO_BUCKET_JOB, str(file_name))
        else:
            logger.info(f"remove_job_from_minio: Bucket does not exist")

