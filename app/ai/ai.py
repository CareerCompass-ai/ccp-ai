from openai import OpenAI

import numpy as np
import httpx
import time

from config.config import ROOT_FOLDER
from constant.ai import OPENAI_API_KEY, OPENAI_EMBEDDING_MODEL, OPENAI_COMPLETION_MODEL, SUMMARIZE_JOB_DESCRIPTION_PROMPT, SUMMARIZE_RESUME_PROMPT

openai_client = OpenAI(api_key=OPENAI_API_KEY)

def get_embedding(input, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            response = openai_client.embeddings.create(input=input["summarized_content"], model=OPENAI_EMBEDDING_MODEL)

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

def get_job_summarized(input, max_retries=3):
    retries = 0
    content = SUMMARIZE_JOB_DESCRIPTION_PROMPT.format(input=input["description"])
    while retries < max_retries:
        try:
            response = openai_client.chat.completions.create(
                model=OPENAI_COMPLETION_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant designed to summarize the content of a job description"},
                    {"role": "user", "content": content}
                ],
                # temperature=0.2,
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

def get_resume_summarized(input, max_retries=3):
    retries = 0
    content = SUMMARIZE_RESUME_PROMPT.format(input=input["description"])
    while retries < max_retries:
        try:
            response = openai_client.chat.completions.create(
                model=OPENAI_COMPLETION_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant designed to summarize the content of a resume"},
                    {"role": "user", "content": content}
                ],
                # temperature=0.2,
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
