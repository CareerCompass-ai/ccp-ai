import weaviate
import constant.config as constant
import constant.ai as ai_constant

class WeaviateVDB:
    WEAVIATE_URL = constant.WEAVIATE_URL
    WEAVIATE_PORT = constant.WEAVIATE_PORT
    WEAVIATE_API_KEY = constant.WEAVIATE_API_KEY
    OPENAI_API_KEY = ai_constant.OPENAI_API_KEY

    @staticmethod
    def setup_weaviate_connection() -> weaviate.WeaviateClient:
        return weaviate.connect_to_custom(
            http_host=constant.SERVER_IP,
            http_port=WeaviateVDB.WEAVIATE_PORT,
            http_secure=False,
            auth_credentials=weaviate.auth.AuthApiKey(WeaviateVDB.WEAVIATE_API_KEY),
            headers={
                "X-OpenAI-Api-Key": WeaviateVDB.OPENAI_API_KEY
            }
        )
