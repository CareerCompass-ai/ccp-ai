from pydantic import BaseModel

class DeleteClassRequest(BaseModel):
    collection_name: str