import json
import time

import httpx
import numpy as np
from openai import OpenAI

import constant.ai as constant
from pkg.logging import logger
from app.dto import ai
class AI:
    def __init__(self, api_key=constant.OPENAI_API_KEY, embedding_model=constant.OPENAI_EMBEDDING_MODEL, completion_model=constant.OPENAI_COMPLETION_MODEL):
        self.openai_client = OpenAI(api_key=api_key)
        self.embedding_model = embedding_model
        self.completion_model = completion_model
        self.beast_completion_model = constant.OPENAI_BEAST_COMPLETION_MODEL
        self.job_question_and_answering_prompt = constant.JOB_QUESTION_AND_ANSWERING_PROMPT

    async def create_assistant(self, file_path, max_retries=3):
        retries = 0
        while retries < max_retries:
            try:

                file = self.openai_client.files.create(
                    file=open(file_path, "rb"),
                    purpose='assistants'
                )
                assistant = self.openai_client.beta.assistants.create(
                    name="Data Visualization",
                    instructions=f"You are a helpful AI assistant who makes interesting visualizations based on data." 
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
                            "file_ids": [file.id]
                        }
                    }
                )
                return assistant.id, file.id
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 400:
                    logger.error(f"Bad request error: {e}")
                else:
                    logger.info(f"Request to OpenAI API failed. Retrying...")
                    retries += 1
                    time.sleep(2)
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
                    time.sleep(2)
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
                is_running = True
                while is_running:
                    run_status = self.openai_client.beta.threads.runs.retrieve(
                        thread_id=input.thread_id, 
                        run_id=run.id
                    )
                    is_running = run_status.status != "completed"
                    if is_running:
                        #TODO: Check 
                        time.sleep(0.5)  # Sleep for a bit before checking again

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
                        _res.image = content_block.image_file.file_id
                return _res

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 400:
                    logger.error(f"Bad request error: {e}")
                    break
                else:
                    logger.info(f"Request to OpenAI API failed. Retrying... ({retries+1}/{max_retries})")
                    retries += 1
                    time.sleep(2)

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
                    time.sleep(2)
        logger.info("Exceeded maximum number of retries. Please try again later.")
        return None

    async def get_answer(self, data, previous_context, question, max_retries=3):
        retries = 0
        input_text = "\n".join([str(item) for item in data])
        
        prompt = (
            f"{self.job_question_and_answering_prompt}"
            f"Previous chat:\n"
            f"{previous_context}\n\n"
            f"Data:\n"
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
                    max_tokens=4096,
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
                    time.sleep(2)
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
                    time.sleep(2) 
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
                    time.sleep(2) 
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
                    time.sleep(2) 
        logger.info(f"Exceeded maximum number of retries. Please try again later.")
        return None
    
    async def get_acronyms_and_abbreviation_of_job(self, input:str, max_retries=3) -> str:
        retries = 0
        prompt = constant.GET_ACRONYMS_AND_ABBREVIATION_PROMPT
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
                    time.sleep(2) 
        logger.info(f"Exceeded maximum number of retries. Please try again later.")
        return None
