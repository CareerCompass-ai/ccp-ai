from pydantic import BaseModel


class DeleteClassRequest(BaseModel):
    collection_name: str

class ManualSyncJobRequest(BaseModel):
    ids: list[int]