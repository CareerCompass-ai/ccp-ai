import weaviate
import constant.config as constant
import constant.ai as ai_constant

class WeaviateVDB:
    WEAVIATE_URL = constant.WEAVIATE_URL
    WEAVIATE_PORT = constant.WEAVIATE_PORT
    WEAVIATE_API_KEY = constant.WEAVIATE_API_KEY

    jobClass = {
        "class": "Job",
        "vectorizer": "text2vec-openai",
        "vectorIndexConfig": {
            "distance": "cosine",
        },
        "moduleConfig": {
            "text2vec-openai": {
                "model": "text-embedding-3-small",
                "dimensions": 1536,
                "type": "text",
            },
            "generative-openai": {}
        },
        # "properties": [
        # # {
        # #     "name": "title",
        # #     "dataType": ["text"]
        # # },
        # # {
        # #     "name": "chunk",
        # #     "dataType": ["text"]
        # # },
        # # {
        # #     "name": "chunk_no",
        # #     "dataType": ["int"]
        # # },
        # # {
        # #     "name": "url",
        # #     "dataType": ["text"],
        # #     "tokenization": "field"
        # # },
        # ],
    }

    jobQnAClass = {
        "class": "JobQnA",
        "description": "Job Collection for Question and Answer",
        "vectorizer": "text2vec-openai",
        "moduleConfig": {
            "qna-openai": {
            "model": "gpt-3.5-turbo-instruct",
            "maxTokens": 16385,
            "temperature": 0.0,
            "topP": 1,
            "frequencyPenalty": 0.0,
            "presencePenalty": 0.0
            }
        },
        "properties": [
            {
            "dataType": [
                "text"
            ],
            "description": "Content that will be vectorized",
            "name": "s_content"
            }
        ]
    }

    @staticmethod
    def setup_weaviate_connection() -> weaviate.WeaviateClient:
        return weaviate.connect_to_custom(
            http_host=constant.SERVER_IP,
            http_port=WeaviateVDB.WEAVIATE_PORT,
            http_secure=False,
            grpc_host=constant.SERVER_IP,
            grpc_port=50051,
            grpc_secure=False,
            auth_credentials=weaviate.auth.AuthApiKey(WeaviateVDB.WEAVIATE_API_KEY),
            headers={
                "X-OpenAI-Api-Key": ai_constant.OPENAI_API_KEY
            }
        )
