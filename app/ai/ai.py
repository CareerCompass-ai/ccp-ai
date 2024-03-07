from openai import OpenAI

import numpy as np

import httpx
import time
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="./builders/.base.env")
openai_api_key = str(os.getenv("OPENAI_KEY"))

openai_client = OpenAI(api_key=openai_api_key)

def get_embedding(input_text, max_retries=5):
    retries = 0
    while retries < max_retries:
        try:
            response = openai_client.embeddings.create(input=input_text, model="text-embedding-ada-002", timeout=60.0).data[0]
            response_vector = np.array(response.embedding)
            return response_vector
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