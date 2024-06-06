from pydantic import BaseModel
from typing import List

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
    user_question: str
    your_answer: str

class JobQnARequest(BaseModel):
    job_ids: list[int]
    question: str = ""
    previous_context: list[PreviousContextItem] = []

class JobQnAResponse(BaseModel):
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
    message: str = ""

class ListAssistantResponse(BaseModel):
    data: List[AssistantResponse]