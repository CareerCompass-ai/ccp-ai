from pydantic import BaseModel

class CreateQnARequest(BaseModel):
    list_job_ids: list[int]

class CreateQnAResponse(BaseModel):
    message: str = ""
    collection_name: str = ""

class QuestionAndAnswerRequest(BaseModel):
    collection_name: str = ""
    question: str = ""

class QuestionAndAnswerResponse(BaseModel):
    collection_name: str = ""
    answer: str = ""

class AssistantResponse(BaseModel):
    assistant_id: str
    thread_id: str
    tmp: str = ""