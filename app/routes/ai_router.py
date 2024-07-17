import os
from fastapi import status, HTTPException, APIRouter, Form, Depends
import traceback
from config import postgres
import constant.config as minio_constant
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from qdrant_client.http.models import PointStruct
from qdrant_client.conversions.common_types import VectorParams
from sqlalchemy.exc import SQLAlchemyError

from fastapi import APIRouter, HTTPException, status
from qdrant_client.conversions.common_types import VectorParams
from qdrant_client.http.models import PointStruct
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from app.dto import ai, minio

from app.dto import assistant

from config.postgres import PostgresDB
from sqlalchemy.orm import Session
from datetime import datetime
from app.factory.factory import RepositoryFactory as factory
from config.qdrant import QdrantVDB as qdrant
from pkg.logging import logger

# AI
from .ai_helper import load_docs, split_docs
from .helper import generate_analysis_file

ai_router = APIRouter(
    prefix="/api",
    tags=['AI']
)

ai_helper = factory.get_ai_helper()
job_qdrant_repo = factory.get_job_qdrant_repo()
resume_qdrant_repo = factory.get_resume_qdrant_repo()
minio_repo = factory.get_minio_repo()
qdrant_client = qdrant.setup_qdrant_connection()
assistant_repo = factory.get_assistant_repo()
application_repo = factory.get_application_repo()

# Assistant
@ai_router.post("/assistant/generate", response_model=ai.GenerateAssistantResponse)
async def generate_assistant (
    req: ai.GenerateAssistantRequest,
    db: Session = Depends(PostgresDB.get_db)
):
    try:
        _file_name_job = 'job_' + req.time_from + '-' + req.time_to + '.csv'
        _file_name_user = 'user_' + req.time_from + '-' + req.time_to + '.csv'

        # Check if CSV exist?
        with db.begin():
            try: 
                _file = await assistant_repo.get_by_file_name(db=db, job_file_name=_file_name_job, user_file_name=_file_name_user)
            except SQLAlchemyError:
                db.rollback()
                logger.error(f"get analysis file failed error = {traceback.format_exc()}")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))


        #If exist
        if _file is not None:
            #Get file from minio
            await minio_repo.get_object(minio_constant.MINIO_BUCKET_ASSISTANT, _file_name_job)
            await minio_repo.get_object(minio_constant.MINIO_BUCKET_ASSISTANT, _file_name_user)

        else:
            #Generate CSV
            with db.begin():
                try: 
                    await generate_analysis_file(db=db, time_from=req.time_from, time_to=req.time_to, file_name_job=_file_name_job, file_name_user=_file_name_user)

                except SQLAlchemyError:
                    db.rollback()
                    logger.error(f"generate analysis file failed error = {traceback.format_exc()}")
                    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))
                
            #Upload MinIO
            await minio_repo.upload(
                minio.UploadMinioRequest(bucket_name=minio_constant.MINIO_BUCKET_ASSISTANT, temp_path=_file_name_job, file_name=_file_name_job)
            )

            await minio_repo.upload(
                minio.UploadMinioRequest(bucket_name=minio_constant.MINIO_BUCKET_ASSISTANT, temp_path=_file_name_user, file_name=_file_name_user)
            )

        #Create assistant & thread
        #Insert into db
        #Remove all assistant exist??
        assistant_id, file_ids = await ai_helper.create_assistant(file_paths=[_file_name_job, _file_name_user], time_from=req.time_from, time_to=req.time_to)

        thread_id = await ai_helper.create_thread()

        now = datetime.now()

        record = assistant.AssistantBase (
            assistant_id=assistant_id,
            thread_id=thread_id,
            job_file_id=file_ids[0],
            user_file_id=file_ids[1],
            time_from=now,
            time_to=now,
            created_at=now,
            updated_at=now,
            job_file_name=_file_name_job,
            user_file_name=_file_name_user
        )

        os.remove(_file_name_job)
        os.remove(_file_name_user)
        
        with db.begin():
            try:
                await assistant_repo.create(session=db, input=record)
                db.commit()
                return ai.GenerateAssistantResponse (
                    assistant_id=assistant_id,
                    thread_id=thread_id,
                    tmp="Sucessfully!"
                )
            except SQLAlchemyError:
                db.rollback()
                #TODO: Remove Assistant and Thread
                logger.error(f"generate assistant failed error = {traceback.format_exc()}")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))
    except Exception:
        logger.error(f"generate_assistant failed error = {traceback.format_exc()}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Oops, sorry, our server went wrong")
        



@ai_router.post("/assistant/questioning", response_model=ai.AssistantResponse)
async def assistant_questioning(req: ai.AssistantQuestionRequest):
    try:
        response = await ai_helper.get_assistant_answer(input=req)

        if response["status"] == "success":
            return response["data"]
        elif response["status"] == "error":
            if response["message"] == "Assistant run timed out":
                raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail=response["message"])
            elif response["message"] == "Assistant run failed":
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=response["message"])
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=response["message"])

    except HTTPException as http_exception:
        raise http_exception

    except Exception as e:
        logger.error(f"assistant_questioning failed error = {traceback.format_exc()}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Oops, sorry, our server went wrong")
# Flow:
# Note: different date time range will have different assistant
# 1. call load_analysis to get file, save file_name to database, next time check exist? if exist note: file has named follow date range then upload the analysis.file to openai -> file.id
# 2. Get the file.id from openai response
# 3. Save the file_name and file.id to the database
# 4. Create a new assistant with the file.id
# 5. Save the assistant.id to the database
# 6. Create thread
# 7. Save the thread.id to the database
# 8. When user enter chat -> create message with thread.id, run the thread with thread_id and assistant_id, while loop until the thread is done
# 9. Return the response


# Question and Answering
# REF: https://medium.com/@shubhama94262/building-a-multiple-choice-question-app-using-langchain-and-llm-model-d59839fd1150
# REF: https://cookbook.openai.com/examples/vector_databases/qdrant/qa_with_langchain_qdrant_and_openai
# REF: https://forum.bubble.io/t/any-idea-how-to-break-large-pdfs-into-chunks-for-open-ai-s-davinci-model/254365
@ai_router.post("/qna/generate", response_model=ai.CreateQnAResponse, status_code=status.HTTP_201_CREATED)
async def generate_qna(req: ai.CreateQnARequest):
    try:
        # Retrieve job list from req.list_job_ids
        data = await job_qdrant_repo.list_jobs_by_ids(req.list_job_ids)

        # Create a temporary PDF file with job list
        modified_data = []
        for job in data:
            job_dict = job.model_dump()
            job_dict.pop('display_content', None)
            job_dict.pop('content_url', None)
            job_dict.pop('common_job_title', None)
            job_dict.pop('recruiter_id', None)
            job_dict.pop('file_name', None)
            modified_data.append(job_dict)

        # Create a buffer to hold the PDF
        buffer = BytesIO()

        # Use SimpleDocTemplate to create the PDF
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        for job in modified_data:
            elements.append(Paragraph(f"Job Title: {job['job_title']}", styles['Heading4']))
            elements.append(Paragraph(f"Job ID: {job['id']}", styles['Heading5']))

            elements.append(Paragraph(
                "Job Description: A comprehensive overview of the responsibilities and duties involved in this role.",
                styles['Italic']))
            elements.append(Paragraph(f"Content: {job['content']}", styles['Normal']))
            elements.append(Spacer(1, 3))

            elements.append(Paragraph(
                "Job Tags: The skills, technologies, and frameworks that are required or expected for this job position.",
                styles['Italic']))
            elements.append(Paragraph(f"Job Tags: {', '.join(job['job_tags'])}", styles['Normal']))
            elements.append(Spacer(1, 3))

            elements.append(Paragraph(
                "Salary Range: The salary range offered for this position, indicating the minimum and maximum salary.",
                styles['Italic']))
            elements.append(Paragraph(f"Salary From: {job['salary_from']}", styles['Normal']))
            elements.append(Paragraph(f"Salary To: {job['salary_to']}", styles['Normal']))
            elements.append(Spacer(1, 3))

            elements.append(Paragraph(
                "Job Type: The nature of the employment, such as full-time, part-time, or contract.",
                styles['Italic']))
            elements.append(Paragraph(f"Job Type: {job['job_type']}", styles['Normal']))
            elements.append(Spacer(1, 3))

            elements.append(Paragraph(
                "Company Type: The category of the company, such as whether it is product-based or service-based.",
                styles['Italic']))
            elements.append(Paragraph(f"Company Type: {job['company_type']}", styles['Normal']))
            elements.append(Spacer(1, 3))

            elements.append(Paragraph(
                "Address: The physical location of the company's office where the job is based.",
                styles['Italic']))
            elements.append(Paragraph(f"Address: {job['address']}", styles['Normal']))
            elements.append(Spacer(1, 3))

            elements.append(Paragraph(
                "City: The city where the company's office is located.",
                styles['Italic']))
            elements.append(Paragraph(f"City: {job['city_name']}", styles['Normal']))
            elements.append(Spacer(1, 3))

            elements.append(Paragraph(
                "Country: The country where the company's office is located.",
                styles['Italic']))
            elements.append(Paragraph(f"Country: {job['country_name']}", styles['Normal']))
            elements.append(Spacer(1, 3))

            elements.append(Paragraph(
                "Hiring Level: The level of experience required for this position, such as entry-level, mid-level, or senior.",
                styles['Italic']))
            elements.append(Paragraph(f"Hiring Level: {job['hiring_level']}", styles['Normal']))
            elements.append(Spacer(1, 3))

            elements.append(Paragraph(
                "Number of Applicants: The total number of applicants who have applied for this position so far.",
                styles['Italic']))
            elements.append(Paragraph(f"Number of Applicants: {job['applied_count']}", styles['Normal']))
            elements.append(Spacer(1, 3))

            elements.append(Paragraph(
                "Work Place: The working environment, indicating whether the job is on-site, remote, or hybrid.",
                styles['Italic']))
            elements.append(Paragraph(f"Work Place: {job['work_place']}", styles['Normal']))
            elements.append(Spacer(1, 3))

            elements.append(Paragraph(
                "Is Hiring: Indicates whether the company is currently accepting applications for this position.",
                styles['Italic']))
            elements.append(Paragraph(f"Is Hiring: {job['is_hiring']}", styles['Normal']))
            elements.append(Spacer(1, 3))

            elements.append(Paragraph(
                "Opened Date: The date when the job listing was first made available to applicants.",
                styles['Italic']))
            elements.append(Paragraph(f"Opened Date: {job['opened_date']}", styles['Normal']))
            elements.append(Spacer(1, 3))

            elements.append(Paragraph(
                "Closed Date: The date when the job listing will no longer accept applications.",
                styles['Italic']))
            elements.append(Paragraph(f"Closed Date: {job['closed_date']}", styles['Normal']))
            elements.append(Spacer(1, 3))

            elements.append(Paragraph(
                "Created At: The date and time when the job listing was originally created.",
                styles['Italic']))
            elements.append(Paragraph(f"Created At: {job['created_at']}", styles['Normal']))
            elements.append(Spacer(1, 3))

            elements.append(Paragraph(
                "Updated At: The date and time when the job listing was last updated.",
                styles['Italic']))
            elements.append(Paragraph(f"Updated At: {job['updated_at']}", styles['Normal']))
            elements.append(Spacer(1, 3))

            elements.append(Paragraph("----------", styles['Normal']))
            elements.append(Spacer(1, 12))

        # TEMP TEMPLATE v1
        # for job in modified_data:
        #     elements.append(Paragraph(f"Job ID: {job['id']}", styles['Normal']))
        #     elements.append(Paragraph(f"Job Title: {job['job_title']}", styles['Normal']))
        #     elements.append(Paragraph(f"Content: {job['content']}", styles['Normal']))
        #     elements.append(Paragraph(f"Is Hiring: {job['is_hiring']}", styles['Normal']))
        #     elements.append(Paragraph(f"Opened Date: {job['opened_date']}", styles['Normal']))
        #     elements.append(Paragraph(f"Closed Date: {job['closed_date']}", styles['Normal']))
        #     elements.append(Paragraph(f"Salary From: {job['salary_from']}", styles['Normal']))
        #     elements.append(Paragraph(f"Salary To: {job['salary_to']}", styles['Normal']))
        #     elements.append(Paragraph(f"Job Type: {job['job_type']}", styles['Normal']))
        #     elements.append(Paragraph(f"Company Type: {job['company_type']}", styles['Normal']))
        #     elements.append(Paragraph(f"Address ID: {job['address_id']}", styles['Normal']))
        #     elements.append(Paragraph(f"Hiring Level: {job['hiring_level']}", styles['Normal']))
        #     elements.append(Paragraph(f"Number of Applicants: {job['applied_count']}", styles['Normal']))
        #     elements.append(Paragraph(f"Work Place: {job['work_place']}", styles['Normal']))
        #     elements.append(Paragraph(f"Created At: {job['created_at']}", styles['Normal']))
        #     elements.append(Paragraph(f"Updated At: {job['updated_at']}", styles['Normal']))
        #     elements.append(Spacer(1, 6))
        #     elements.append(Paragraph("----------", styles['Normal']))
        #     elements.append(Spacer(1, 6))

        # TEMP TEMPLATE v2
        # for job in modified_data:
        #     elements.append(Paragraph(f"Job ID: {job['id']}", styles['Normal']))
        #     elements.append(Paragraph(f"Job Title: {job['job_title']}", styles['Normal']))
        #     elements.append(Paragraph(f"Content: {job['content']}", styles['Normal']))
        #     elements.append(Paragraph(f"Is Hiring: {job['is_hiring']}", styles['Normal']))
        #     elements.append(Paragraph(f"Opened Date: {job['opened_date']}", styles['Normal']))
        #     elements.append(Paragraph(f"Closed Date: {job['closed_date']}", styles['Normal']))
        #     elements.append(Paragraph(f"Salary From: {job['salary_from']}", styles['Normal']))
        #     elements.append(Paragraph(f"Salary To: {job['salary_to']}", styles['Normal']))
        #     elements.append(Paragraph(f"Job Type: {job['job_type']}", styles['Normal']))
        #     elements.append(Paragraph(f"Company Type: {job['company_type']}", styles['Normal']))
        #     elements.append(Paragraph(f"Address ID: {job['address_id']}", styles['Normal']))
        #     elements.append(Paragraph(f"Hiring Level: {job['hiring_level']}", styles['Normal']))
        #     elements.append(Paragraph(f"Number of applicants: {job['applied_count']}", styles['Normal']))
        #     elements.append(Paragraph(f"Work Place: {job['work_place']}", styles['Normal']))
        #     elements.append(Paragraph(f"Created At: {job['created_at']}", styles['Normal']))
        #     elements.append(Paragraph(f"Updated At: {job['updated_at']}", styles['Normal']))
        #     elements.append(Spacer(1, 6))
        #     elements.append(Paragraph("----------", styles['Normal']))
        #     elements.append(Spacer(1, 6))

        doc.build(elements)
        buffer.seek(0)

        # Define the collection name
        collection_name = f"qna_{'_'.join(map(str, sorted(req.list_job_ids, reverse=True)))}"

        # Save the buffer as a file
        temp_pdf_path = "tmp/job_storage/temp_data.pdf"
        with open(temp_pdf_path, "wb") as f:
            f.write(buffer.getvalue())

        # Load the PDF file
        documents = await load_docs("tmp/job_storage/")

        # Split the documents into chunks
        chunks = await split_docs(documents)

        await minio_repo.upload(minio.UploadMinioRequest(
            bucket_name="job-qna-storage",
            file_name=f"{collection_name}.pdf",
            temp_path=temp_pdf_path
        ))

        # Delete the temporary PDF file after splitting into chunks
        os.remove(temp_pdf_path)

        # Embed each chunk
        embeddings = [await ai_helper.get_embedding(chunk.page_content) for chunk in chunks]

        vectors_config = VectorParams(
            size=len(embeddings[0]),
            distance="Cosine"       
        )

        # Create the collection in Qdrant if it does not exist, NOTE: this recreate_collection is deprecated
        qdrant_client.recreate_collection(
            collection_name=collection_name,
            vectors_config=vectors_config,
        )

        # Add embeddings to the Qdrant collection
        points = []
        for i, embedding in enumerate(embeddings):
            point = PointStruct(id=i, vector=embedding, payload={"text": chunks[i].page_content})
            points.append(point)

        qdrant_client.upsert(collection_name=collection_name, points=points)

        # Return response with the collection name
        return ai.CreateQnAResponse(
            message="QnA created successfully",
            collection_name=collection_name
        )

    except Exception:
        logger.error(f"create_qna failed error = {traceback.format_exc()}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Oops, sorry, our server went wrong")

@ai_router.post("/qna/generate_v2", response_model=ai.CreateQnAResponse, status_code=status.HTTP_201_CREATED)
async def generate_qna_v2(req: ai.CreateQnARequest):
    try:
        # Retrieve job list from req.list_job_ids
        data = await job_qdrant_repo.list_jobs_by_ids(req.list_job_ids)

        modified_data = []
        for job in data:
            job_dict = job.model_dump()
            job_dict.pop('display_content', None)
            job_dict.pop('content_url', None)
            job_dict.pop('common_job_title', None)
            job_dict.pop('recruiter_id', None)
            job_dict.pop('file_name', None)
            job_dict.pop('s_content', None)
            job_dict.pop('combined_content', None)
            job_dict.pop('is_applied', None)
            job_dict.pop('is_saved', None)
            job_dict.pop('matching_score', None)
            modified_data.append(job_dict)

        # Convert modified data to strings
        string_data = [str(job) for job in modified_data]

        # Define the collection name
        collection_name = f"qna_{'_'.join(map(str, sorted(req.list_job_ids, reverse=True)))}"

        # Embed each string
        embeddings = [await ai_helper.get_embedding(chunk) for chunk in string_data]

        vectors_config = VectorParams(
            size=len(embeddings[0]),
            distance="Cosine"       
        )

        # Create the collection in Qdrant if it does not exist
        qdrant_client.recreate_collection(
            collection_name=collection_name,
            vectors_config=vectors_config,
        )

        # Add embeddings to the Qdrant collection
        points = []
        for i, embedding in enumerate(embeddings):
            point = PointStruct(id=i, vector=embedding, payload={"text": string_data[i]})
            points.append(point)

        qdrant_client.upsert(collection_name=collection_name, points=points)

        # Return response with the collection name
        return ai.CreateQnAResponse(
            message="QnA created successfully",
            collection_name=collection_name
        )

    except Exception:
        logger.error(f"create_qna failed error = {traceback.format_exc()}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Oops, sorry, our server went wrong")

# RAG
@ai_router.post("/qna/questioning_v1", response_model=ai.QuestionAndAnswerResponse)
async def questioning_v1(req: ai.QuestionAndAnswerRequest):
    try:
        # Calculate the embedding for the query
        query_embedding = await ai_helper.get_embedding(req.question)

        # Retrieve relevant documents from Qdrant
        relevant_docs = qdrant_client.search(
            collection_name=req.collection_name,
            query_vector=query_embedding,
            limit=2 # currently limit to 2 relevant docs
        )

        # Prepare input for OpenAI model
        input_documents = [doc.payload["text"] for doc in relevant_docs]
        
        # Get answer from OpenAI model
        answer = await ai_helper.get_answer_v1(req.question, input_documents)
        
        return ai.QuestionAndAnswerResponse(
            collection_name=req.collection_name,
            answer=answer
        )

    except Exception:
        logger.error(f"questioning failed error = {traceback.format_exc()}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Oops, sorry, our server went wrong")

@ai_router.post("/ai/jobs/questioning", response_model=ai.JobQnAResponse)
async def questioning(req: ai.JobQnARequest):
    try:
        data = await job_qdrant_repo.list_jobs_by_ids(req.job_ids)

        # Remove unnecessary fields
        modified_data = []
        for job in data:
            job_dict = job.model_dump()
            job_dict.pop('address_id', None)
            job_dict.pop('recruiter_id', None)
            job_dict.pop('file_name', None)
            job_dict.pop('s_content', None)
            job_dict.pop('display_content', None)
            job_dict.pop('combined_content', None)
            job_dict.pop('recruiter_id', None)
            job_dict.pop('is_applied', None)
            job_dict.pop('is_saved', None)

            modified_data.append(job_dict)

        # previous_context_formatted = "\n".join(
        #     [
        #         f"user_question: {item.question}\nyour_answer: {item.answer}\n"
        #         for item in req.prev
        #     ]
        # )
        
        # previous_context_formatted = "\n".join(
        #     [
        #         f"user_question: {item.question}\nyour_answer: {item.answer}\n"
        #         for item in req.prev
        #     ]
        # ) + f"\nFocus specifically on the job discussed previously: {req.prev[-1].answer if req.prev else ''}"

        # answer = await ai_helper.get_answer(modified_data, previous_context_formatted, req.question)

        if req.prev:
            previous_context_formatted = "\n".join(
                [
                    f"user_question: {item.question}\nyour_answer: {item.answer}\n"
                    for item in req.prev
                ]
            )
            previous_context_section = f"Previous conversation:\n{previous_context_formatted}\nFocus specifically on the job discussed previously: {req.prev[-1].answer}"
        else:
            previous_context_section = ""

        answer = await ai_helper.get_answer(modified_data, previous_context_section, req.question)

        # TODO: Count remain token -> return a field to indicate whether the user has run out of tokens

        return ai.JobQnAResponse(
            answer=answer
        )

    except Exception:
        logger.error(f"questioning failed error = {traceback.format_exc()}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Oops, sorry, our server went wrong")
    
@ai_router.post("/ai/resumes/questioning", response_model=ai.ResumeQnAResponse)
async def resumes_questioning(
        req: ai.ResumeQnARequest,
        db: Session = Depends(postgres.PostgresDB.get_db)
    ):
    try:
        # get all resumes applied for the job
        applied_resume_ids = await application_repo.list_resume_ids_by_job_id(db=db, job_id=req.job_id)

        # check if any of the req.resume_ids is not in the list of resumes applied for the job
        if any(resume_id not in applied_resume_ids for resume_id in req.resume_ids):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to access this resource")
        
        data = await resume_qdrant_repo.list_resumes_by_ids(req.resume_ids)

        # Remove unnecessary fields
        modified_data = []
        for resume in data:
            resume_dict = resume.model_dump()
            resume_dict.pop('matching_score', None)
            resume_dict.pop('s_content', None)
            resume_dict.pop('matching_score', None)
            modified_data.append(resume_dict)

        if req.prev:
            previous_context_formatted = "\n".join(
                [
                    f"user_question: {item.question}\nyour_answer: {item.answer}\n"
                    for item in req.prev
                ]
            )
            previous_context_section = f"Previous conversation:\n{previous_context_formatted}\nFocus specifically on the resumes or candidates discussed previously: {req.prev[-1].answer}"
        else:
            previous_context_section = ""

        answer = await ai_helper.get_resume_answer(modified_data, previous_context_section, req.question)

        # TODO: Count remain token -> return a field to indicate whether the user has run out of tokens

        return ai.ResumeQnAResponse(
            answer=answer
        )

    except Exception:
        logger.error(f"questioning failed error = {traceback.format_exc()}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Oops, sorry, our server went wrong")
    
@ai_router.post("/ai/resume/enhance", response_model=ai.GetEnhanceResumeResponse)
async def get_enhance_resume(req: ai.GetEnhanceResumeRequest):
    try:
        data = await ai_helper.get_enhance_resume_content(req.content)

        if data is None:
            return ai.GetEnhanceResumeResponse(message=[])

        return ai.GetEnhanceResumeResponse(
            message=data
        )

    except Exception as e:
        logger.error(f"get_enhance_resume failed: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Oops, sorry, our server went wrong")
