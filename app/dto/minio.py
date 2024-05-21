from pydantic import BaseModel

class UploadMinioRequest(BaseModel):
    bucket_name: str
    temp_path: str
    file_name: str
class UploadMinioResponse(BaseModel):
    url: str 
