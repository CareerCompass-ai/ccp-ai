from pydantic import BaseModel
from typing import List, Optional

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
    prev: list[PreviousContextItem] = []

class JobQnAResponse(BaseModel):
    answer: str = ""

class ResumeQnARequest(BaseModel):
    resume_ids: list[int]
    question: str = ""
    prev: list[PreviousContextItem] = []

class ResumeQnAResponse(BaseModel):
    answer: str = ""

class GenerateAssistantResponse(BaseModel):
    assistant_id: str
    thread_id: str
    tmp: str = ""

class AssistantQuestionRequest(BaseModel):
    assistant_id: str
    thread_id: str
    message: str = ""

class AssistantResponse(BaseModel):
    message: Optional[str] = None
    image: Optional[str] = None

class ListAssistantResponse(BaseModel):
    data: List[AssistantResponse]

class GenerateAssistantRequest(BaseModel):
    time_from: str
    time_to: str