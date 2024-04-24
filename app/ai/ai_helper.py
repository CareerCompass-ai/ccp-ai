from openai import OpenAI

import numpy as np
import httpx
import time

import constant.ai as constant

class AI:
    def __init__(self, api_key=constant.OPENAI_API_KEY, embedding_model=constant.OPENAI_EMBEDDING_MODEL, completion_model=constant.OPENAI_COMPLETION_MODEL):
        self.openai_client = OpenAI(api_key=api_key)
        self.embedding_model = embedding_model
        self.completion_model = completion_model

    def get_embedding(self, input, max_retries=3):
        retries = 0
        while retries < max_retries:
            try:
                response = self.openai_client.embeddings.create(input=input, model=self.embedding_model)
                
                return np.array(response.data[0].embedding)
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 400:
                    print("Bad request error:", e)
                    break
                else:
                    print("Request to OpenAI API failed. Retrying...")
                    retries += 1
                    time.sleep(2) 
        print("Exceeded maximum number of retries. Please try again later.")
        return None

    def get_summarized_content(self, input:str, prompt:str, type:str, max_retries=3):
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
                    print("Bad request error:", e)
                    break
                else:
                    print("Request to OpenAI API failed. Retrying...")
                    retries += 1
                    time.sleep(2) 
        print("Exceeded maximum number of retries. Please try again later.")
        return None

    def get_job_summarized(self, input, max_retries=3):
        return self.get_summarized_content(input, constant.SUMMARIZE_JOB_DESCRIPTION_PROMPT, "job", max_retries)

    def get_resume_summarized(self, input, max_retries=3):
        return self.get_summarized_content(input, constant.SUMMARIZE_RESUME_PROMPT, "resume", max_retries)
    
    def get_common_job_title(self, input: str, max_retries=3):
        retries = 0
        content = "Job title '{}' is considered to belong to which position in the following list (Software Engineer, Product Owner/Product Manager/Business Analyst, Project Manager/Project Lead, UI/UX Designer, Tester/QA-QC, System Engineer, DevOps Engineer, Data/AI & MLs). If not, write it down to (Other Positions). No need to repeat This position belongs to... Just answer what position it is.".format(input)
        while retries < max_retries:
            try:
                response = self.openai_client.chat.completions.create(
                    model=self.completion_model,
                    messages=[
                        # {"role": "system", "content": f"You are a helpful assistant designed to summarize the content of {type}"},
                        {"role": "user", "content": content}
                    ],
                    top_p=0.2,
                )

                return response.choices[0].message.content.strip()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 400:
                    print("Bad request error:", e)
                    break
                else:
                    print("Request to OpenAI API failed. Retrying...")
                    retries += 1
                    time.sleep(2) 
        print("Exceeded maximum number of retries. Please try again later.")
        return None
