import traceback
import constant.config as constant

from typing import Optional
from minio import Minio
from minio.error import S3Error

from app.dto import minio

from pkg.logging import logger

class MinioRepository:
    def __init__(self):
        self.client = Minio (
            endpoint= constant.MINIO_URL,
            access_key=constant.MINIO_USERNAME,
            secret_key=constant.MINIO_PASSWORD,
            secure=False
        )

    async def upload(self, input: Optional[minio.UploadMinioRequest]) -> minio.UploadMinioResponse:
        try:
            if not self.client.bucket_exists(input.bucket_name):
                self.client.make_bucket(input.bucket_name)
                logger.info(f"Bucket {input.bucket_name} created")

            self.client.fput_object(
                input.bucket_name,
                input.file_name,
                input.temp_path
            )

            return minio.UploadMinioResponse(
                url=f"{constant.MINIO_URL}/{input.bucket_name}/{input.file_name}"
            )

        except S3Error as e:
            logger.error(f"upload with bucket:[{input.bucket_name}] with file:[{input.file_name}] failed err: {traceback.format_exc()}")
            raise

    async def generate_presigned_url(self, bucket_name: str, object_name: str) -> str:
        try:
            return self.client.presigned_put_object(bucket_name, object_name)
        except S3Error as err:
            logger.error(f"generate_presigned_url with bucket:[{bucket_name}] with file:[{object_name}] failed err: {traceback.format_exc()}")

    async def remove_object(self, bucket_name, file_name):
        if self.client.bucket_exists(bucket_name):
            self.client.remove_object(bucket_name, str(file_name))
        else:
            logger.error(f"remove_object with bucket:[{bucket_name}] with file:[{file_name}] failed err: {traceback.format_exc()}")

    async def get_object(self, bucket_name, file_name):
        if self.client.bucket_exists(bucket_name):
            self.client.fget_object(bucket_name=bucket_name, object_name=file_name, file_path=file_name)
        else:
            logger.error(f"get_object with bucket:[{bucket_name}] with file:[{file_name}] failed err: {traceback.format_exc()}")
