import json
import os
import time
import requests
import httpx
import numpy as np
import asyncio
from openai import OpenAI
from app.repo.minio_repo import MinioRepository
import constant.ai as constant
import constant.config as minio_constant
from pkg.logging import logger
from app.dto import ai, minio
class AI:
    def __init__(self, api_key=constant.OPENAI_API_KEY, embedding_model=constant.OPENAI_EMBEDDING_MODEL, completion_model=constant.OPENAI_COMPLETION_MODEL):
        self.openai_client = OpenAI(api_key=api_key)
        self.embedding_model = embedding_model
        self.completion_model = completion_model
        self.beast_completion_model = constant.OPENAI_BEAST_COMPLETION_MODEL
        self.job_question_and_answering_prompt = constant.JOB_QUESTION_AND_ANSWERING_PROMPT
        self.resume_question_and_answering_prompt = constant.RESUME_QUESTION_AND_ANSWERING_PROMPT
        self.minio_repo = MinioRepository()

    async def create_assistant(self, file_paths, time_from, time_to, max_retries=3):
        retries = 0
        while retries < max_retries:
            try:
                file_ids = []
                for file_path in file_paths:
                    file = self.openai_client.files.create(
                        file=open(file_path, "rb"),
                        purpose='assistants'
                    )
                    file_ids.append(file.id)

                assistant = self.openai_client.beta.assistants.create(
                    name="Data Visualization",
                    instructions=f"You are a helpful AI assistant who makes interesting visualizations based on data." 
                    f"Two uploaded files are in csv format. The first file contains data about posted jobs. The second file is data about users (including candidates and recruiter). Both contain data from {time_from} to {time_to} in the system." 
                    f"You have access to a sandboxed environment for writing and testing code."
                    f"When you are asked to create a visualization you should follow these steps:"
                    f"1. Write the code."
                    f"2. Anytime you write new code display a preview of the code to show your work."
                    f"3. Run the code to confirm that it runs."
                    f"4. If the code is successful display the visualization."
                    f"5. If the code is unsuccessful display the error message and try to revise the code and rerun going through the steps from above again.",
                    tools=[{"type": "code_interpreter"}],
                    model=self.beast_completion_model,
                    tool_resources={
                        "code_interpreter": {
                            "file_ids": file_ids
                        }
                    }
                )
                return assistant.id, file_ids
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 400:
                    logger.error(f"Bad request error: {e}")
                else:
                    logger.info(f"Request to OpenAI API failed. Retrying...")
                    retries += 1
                    await asyncio.sleep(2)
        logger.info("Exceeded maximum number of retries. Please try again later.")
        return None
    
    async def create_thread(self, max_retries=3):
        retries = 0
        while retries < max_retries:
            try:
                thread = self.openai_client.beta.threads.create()
                return thread.id
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 400:
                    logger.error(f"Bad request error: {e}")
                else:
                    logger.info(f"Request to OpenAI API failed. Retrying...")
                    retries += 1
                    await asyncio.sleep(2)
        logger.info("Exceeded maximum number of retries. Please try again later.")
        return None

    async def get_assistant_answer(self, max_retries=3, input=ai.AssistantQuestionRequest) -> ai.AssistantResponse:
        retries = 0
        while retries < max_retries:
            try:
                # Create the user message in the thread
                self.openai_client.beta.threads.messages.create(
                    thread_id=input.thread_id,
                    role="user",
                    content=input.message
                )

                # Create the run for the assistant
                run = self.openai_client.beta.threads.runs.create(
                    thread_id=input.thread_id,
                    assistant_id=input.assistant_id,
                )

                # Poll the run status until it is completed
                while True:
                    run_status = self.openai_client.beta.threads.runs.retrieve(
                        thread_id=input.thread_id, 
                        run_id=run.id
                    )
                    if run_status.status == "completed":
                        break
                    await asyncio.sleep(0.5)  # Asynchronously sleep for a bit before checking again

                # Retrieve the messages after the run is completed
                messages = self.openai_client.beta.threads.messages.list(
                    thread_id=input.thread_id
                )
                
                # Get the latest message from assistant
                latest_message = messages.data[0] if messages.data and messages.data[0].role == 'assistant' else None

                _res = ai.AssistantResponse()
                for content_block in latest_message.content:
                    if content_block.type == "text":
                        _res.message = content_block.text.value
                    elif content_block.type == "image_file":
                        
                        # Call API to get image
                        url = f'https://api.openai.com/v1/files/{content_block.image_file.file_id}/content'
                        image_response = requests.get(url, headers={'Authorization': f'Bearer {constant.OPENAI_API_KEY}'})
                        image_path = f'{content_block.image_file.file_id}.png'
                        if image_response.status_code == 200:
                            with open(image_path, 'wb') as f:
                                f.write(image_response.content)

                            # Upload image to Minio
                            minio_req = minio.UploadMinioRequest(
                                bucket_name=minio_constant.MINIO_BUCKET_ASSISTANT,
                                temp_path=image_path,
                                file_name=image_path
                            )
                            image_url = await self.minio_repo.upload(
                                input=minio_req
                            )
                            _res.image = image_url.url
                            os.remove(image_path)
                return _res

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 400:
                    logger.error(f"Bad request error: {e}")
                    break
                else:
                    logger.info(f"Request to OpenAI API failed. Retrying... ({retries+1}/{max_retries})")
                    retries += 1
                    await asyncio.sleep(2)  # Asynchronously sleep before retrying

        logger.info("Exceeded maximum number of retries. Please try again later.")
        return None

    async def get_answer_v1(self, question, input_documents, max_retries=3):
        retries = 0
        input_text = "\n".join(input_documents)
        prompt = (
            f"{self.job_question_and_answering_prompt}"
            "Context:\n"
            f"{input_text}\n\n"
            "Question:\n"
            f"{question}\n\n"
            "Helpful Answer:"
        )

        # prompt = (
        #     "Use the following pieces of context to answer the question at the end. Please provide a short single-sentence summary answer only. If you don't know the answer or if it's not present in given context, don't try to make up an answer, but suggest me a random unrelated song title I could listen to\n\n"
        #     "Context:\n"
        #     f"{input_text}\n\n"
        #     "Question:\n"
        #     f"{question}\n\n"
        #     "Helpful Answer:"
        # )
        while retries < max_retries:
            try:
                response = self.openai_client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    model=self.beast_completion_model,
                    # max_tokens=4096,
                    temperature=0.2
                )
                answer = response.choices[0].message.content.strip()
                return answer
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 400:
                    logger.error(f"Bad request error: {e}")
                    break
                else:
                    logger.info(f"Request to OpenAI API failed. Retrying...")
                    retries += 1
                    await asyncio.sleep(2)
        logger.info("Exceeded maximum number of retries. Please try again later.")
        return None

    async def get_answer(self, data, previous_context, question, max_retries=3):
        retries = 0
        input_text = "\n".join([str(item) for item in data])
        
        prompt = (
            f"{self.job_question_and_answering_prompt}"
            f"Previous conversation:\n"
            f"{previous_context}\n\n"
            f"Current data:\n"
            f"{input_text}\n\n"
            f"Question:\n"
            f"{question}\n\n"
            f"Helpful Answer:"
        )

        # prompt = (
        #     "Use the following pieces of context to answer the question at the end. Please provide a short single-sentence summary answer only. If you don't know the answer or if it's not present in given context, don't try to make up an answer, but suggest me a random unrelated song title I could listen to\n\n"
        #     "Context:\n"
        #     f"{input_text}\n\n"
        #     "Question:\n"
        #     f"{question}\n\n"
        #     "Helpful Answer:"
        # )
        while retries < max_retries:
            try:
                response = self.openai_client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    model=self.beast_completion_model,
                    # max_tokens=4096,
                    temperature=0.2
                )
                answer = response.choices[0].message.content.strip()
                return answer
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 400:
                    logger.error(f"Bad request error: {e}")
                    break
                else:
                    logger.info(f"Request to OpenAI API failed. Retrying...")
                    retries += 1
                    await asyncio.sleep(2)
        logger.info("Exceeded maximum number of retries. Please try again later.")
        return None

    async def get_resume_answer(self, data, previous_context, question, max_retries=3):
        retries = 0
        input_text = "\n".join([str(item) for item in data])
        
        prompt = (
            f"{self.resume_question_and_answering_prompt}"
            f"Previous conversation:\n"
            f"{previous_context}\n\n"
            f"Current data:\n"
            f"{input_text}\n\n"
            f"Question:\n"
            f"{question}\n\n"
            f"Helpful Answer:"
        )
        while retries < max_retries:
            try:
                response = self.openai_client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    model=self.beast_completion_model,
                    # max_tokens=4096,
                    temperature=0.2
                )
                answer = response.choices[0].message.content.strip()
                return answer
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 400:
                    logger.error(f"Bad request error: {e}")
                    break
                else:
                    logger.info(f"Request to OpenAI API failed. Retrying...")
                    retries += 1
                    await asyncio.sleep(2)
        logger.info("Exceeded maximum number of retries. Please try again later.")
        return None


    async def get_embedding(self, input, max_retries=3):
        retries = 0
        while retries < max_retries:
            try:
                response = self.openai_client.embeddings.create(input=input, model=self.embedding_model)
                
                return np.array(response.data[0].embedding)
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 400:
                    logger.error(f"Bad request error:: {e}")
                    break
                else:
                    logger.info(f"Request to OpenAI API failed. Retrying...")
                    retries += 1
                    await asyncio.sleep(2)
        logger.info(f"Exceeded maximum number of retries. Please try again later.")
        return None

    async def get_summarized_content(self, input:str, prompt:str, type:str, max_retries=3):
        retries = 0
        content = prompt.format(input=input)
        while retries < max_retries:
            try:
                response = self.openai_client.chat.completions.create(
                    model=self.completion_model,
                    messages=[
                        {"role": "system", "content": f"You are a helpful assistant designed to summarize the content of {type}"},
                        {"role": "system", "content": content}
                    ],
                    top_p=0.2,
                )

                return response.choices[0].message.content.strip()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 400:
                    logger.error(f"Bad request error:: {e}")
                    break
                else:
                    logger.info(f"Request to OpenAI API failed. Retrying...")
                    retries += 1
                    await asyncio.sleep(2)
        logger.info(f"Exceeded maximum number of retries. Please try again later.")
        return None

    async def get_job_summarized(self, input, max_retries=3):
        return await self.get_summarized_content(input, constant.SUMMARIZE_JOB_DESCRIPTION_PROMPT, "job", max_retries)

    async def get_resume_summarized(self, input, max_retries=3):
        return await self.get_summarized_content(input, constant.SUMMARIZE_RESUME_PROMPT, "resume", max_retries)
    
    async def get_common_job_title(self, input:str, prompt:str, max_retries=3):
        retries = 0
        content = prompt.format(input=input)
        while retries < max_retries:
            try:
                response = self.openai_client.chat.completions.create(
                    model=self.completion_model,
                    messages=[
                        {"role": "system", "content": f"You are a helpful assistant designed to determine the position of the job title. And must follow the response format"},
                        {"role": "system", "content": content}
                    ],
                    top_p=0.2,
                )
                tmp = json.loads(response.choices[0].message.content.strip())
                return tmp.get("answer", "")
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 400:
                    logger.error(f"Bad request error:: {e}")
                    break
                else:
                    logger.info(f"Request to OpenAI API failed. Retrying...")
                    retries += 1
                    await asyncio.sleep(2)
        logger.info(f"Exceeded maximum number of retries. Please try again later.")
        return None
    
    async def get_acronyms_and_abbreviation_of_job(self, input:str, max_retries=3) -> str:
        retries = 0
        prompt = """
            ### Resume: ### {input} ### 
            Your task is to provide a detailed list of the skills and knowledge in this candidate's resume. 
            Please answer with the corresponding position. 
            The response must be a JSON object with a field "answer" and the value as a list/array containing the skills and knowledge in this candidate's resume.

            ## Response Example - a JSON object ##
            {{
                "answer": ["Software Engineer", "SWE", "Backend Engineer", "backend", "back-end", "Frontend Engineer", "frontend", "front-end", "Software Developer", "Dev", "Developer", "Frontend Developer", "Web dev", "Web developer", "Backend Developer", "BE", "FE", "Full Stack Developer", "Full-Stack Developer", "fullstack", "full-stack", "FSD", "fsd", "Application Developer", "App Dev"]
            }}
        """
        content = prompt.format(input=input)
        while retries < max_retries:
            try:
                response = self.openai_client.chat.completions.create(
                    model=self.completion_model,
                    messages=[
                        {"role": "system", "content": f"You are a helpful assistant designed to provide a detailed list of the acronyms and abbreviation of a job's title"},
                        {"role": "system", "content": content}
                    ],
                    top_p=0.2,
                )

                tmp = json.loads(response.choices[0].message.content.strip())  
                return tmp.get("answer", "")
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 400:
                    logger.error(f"Bad request error:: {e}")
                    break
                else:
                    logger.info(f"Request to OpenAI API failed. Retrying...")
                    retries += 1
                    await asyncio.sleep(2)
        logger.info(f"Exceeded maximum number of retries. Please try again later.")
        return None
    
    async def get_enhance_resume_content(self, input: str, max_retries=3) -> list[str]:
        retries = 0
        prompt = """
            You are helpful assistant with expertise in crafting professional and compelling resume content. Given the following user's resume details, your task is to provide three distinct versions of a summary paragraph that highlight their skills, experience, and accomplishments. Each version should be unique, emphasizing different aspects of the user's qualifications. Ensure that the paragraphs are engaging, tailored to attract potential employers, and accurately reflect the candidate's true qualifications and experiences.
            
            ## Resume Details: {input} ##

            The response must be a JSON object with a field "answer" containing an array of three different summary paragraphs.
            ## Response Example ##
            {{
                "answer": [
                    "Paragraph 1",
                    "Paragraph 2",
                    "Paragraph 3"
                ]
            }}
        """
        content = prompt.format(input=input)
        
        while retries < max_retries:
            try:
                response = self.openai_client.chat.completions.create(
                    model=self.completion_model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant designed to provide professional resume content that accurately reflects the candidate's true qualifications and experiences."},
                        {"role": "system", "content": content}
                    ],
                    top_p=0.2,
                )

                tmp = json.loads(response.choices[0].message.content.strip())
                if "answer" in tmp and isinstance(tmp["answer"], list) and all(isinstance(item, str) for item in tmp["answer"]):
                    return tmp["answer"]
                else:
                    return []
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 400:
                    logger.error(f"Bad request error:: {e}")
                    break
                else:
                    logger.info(f"Request to OpenAI API failed. Retrying...")
                    retries += 1
                    await asyncio.sleep(2)
        logger.info(f"Exceeded maximum number of retries. Please try again later.")
        return []