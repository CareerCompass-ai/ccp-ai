from qdrant_client import QdrantClient

import constant.config as constant

class QdrantVDB:
    QDRANT_URL = constant.QDRANT_URL
    QDRANT_INDEX_JOB_SEARCH = constant.QDRANT_INDEX_JOB_SEARCH
    QDRANT_INDEX_RESUME_SEARCH = constant.QDRANT_INDEX_RESUME_SEARCH

    @staticmethod
    def setup_qdrant_connection() -> QdrantClient:
        return QdrantClient(
            url=constant.DB_SERVER_IP,
            port=constant.QDRANT_PORT
        )
