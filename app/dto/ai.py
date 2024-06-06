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

class PreviousContextItem(BaseModel):
    question: str
    answer: str

class JobQnARequest(BaseModel):
    job_ids: list[int]
    question: str = ""
    previous_context: list[PreviousContextItem] = []

class JobQnAResponse(BaseModel):
    answer: str = ""

class AssistantResponse(BaseModel):
    tmp: str = ""