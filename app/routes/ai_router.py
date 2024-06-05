import os
from fastapi import status, HTTPException, APIRouter, Form, Depends
import traceback
import constant.config as minio_constant
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from qdrant_client.http.models import PointStruct
from qdrant_client.conversions.common_types import VectorParams
from sqlalchemy.exc import SQLAlchemyError

from pkg.logging import logger
from app.dto import ai, minio
from config.qdrant import QdrantVDB as qdrant
from app.repo.job_qdrant_repo import JobQdrantRepository
from app.repo.minio_repo import MinioRepository
from app.repo.assistant_repo import AssistantRepository

from app.dto import assistant

from config.postgres import PostgresDB
from sqlalchemy.orm import Session
from datetime import datetime

# AI
from .ai_helper import load_docs, split_docs
from ..ai.ai_helper import AI
from .helper import generate_analysis_file

ai_router = APIRouter(
    prefix="/api",
    tags=['AI']
)

ai_helper = AI()
job_qdrant_repo = JobQdrantRepository(index_name=qdrant.QDRANT_INDEX_JOB_SEARCH)
qdrant_client = qdrant.setup_qdrant_connection()
minio_repo = MinioRepository()
assistant_repo = AssistantRepository()

# Assistant
@ai_router.post("/assistant/generate", response_model=ai.AssistantResponse)
async def generate_assistant (
    time_from: str = Form(None),
    time_to: str = Form(None),
    db: Session = Depends(PostgresDB.get_db)
):
    try:
        _file_name = time_from + '-' + time_to + '.csv'

        # Check if CSV exist?
        with db.begin():
            try: 
                _file = await assistant_repo.get_by_file_name(db=db, name=_file_name)
            except SQLAlchemyError:
                db.rollback()
                logger.error(f"get analysis file failed error = {traceback.format_exc()}")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))


        #If exist
        if _file is not None:
            #Get file from minio
            await minio_repo.get_object(minio_constant.MINIO_BUCKET_ASSISTANT, _file_name)
        else:
            #Generate CSV
            with db.begin():
                try: 
                    await generate_analysis_file(db=db, time_from=time_from, time_to=time_to, file_name=_file_name)

                except SQLAlchemyError:
                    db.rollback()
                    logger.error(f"generate analysis file failed error = {traceback.format_exc()}")
                    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))
                
            #Upload MinIO
            upload_response = await minio_repo.upload(
                minio.UploadMinioRequest(bucket_name=minio_constant.MINIO_BUCKET_ASSISTANT, temp_path=_file_name, file_name=_file_name)
            )

        #Create assistant & thread
        #Insert into db
        assistant_id, file_id = await ai_helper.create_assistant(file_path=_file_name)

        thread_id = await ai_helper.create_thread()

        now = datetime.now()

        record = assistant.AssistantBase (
            assistant_id=assistant_id,
            thread_id=thread_id,
            file_id=file_id,
            time_from=now,
            time_to=now,
            created_at=now,
            updated_at=now
        )

        os.remove(_file_name)
        
        with db.begin():
            try:
                await assistant_repo.create(session=db, input=record)
                return ai.AssistantResponse (
                    assistant_id=assistant_id,
                    thread_id=thread_id,
                    tmp="Sucessfully!"
                )
            except SQLAlchemyError:
                db.rollback()
                logger.error(f"generate assistant failed error = {traceback.format_exc()}")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))
    except Exception:
        logger.error(f"generate_assistant failed error = {traceback.format_exc()}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Oops, sorry, our server went wrong")
        



@ai_router.post("/assistant/questioning", response_model=ai.AssistantResponse)
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


@ai_router.post("/qna/questioning", response_model=ai.QuestionAndAnswerResponse)
async def questioning(req: ai.QuestionAndAnswerRequest):
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
        answer = await ai_helper.get_answer(req.question, input_documents)
        
        return ai.QuestionAndAnswerResponse(
            collection_name=req.collection_name,
            answer=answer
        )

    except Exception:
        logger.error(f"questioning failed error = {traceback.format_exc()}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Oops, sorry, our server went wrong")