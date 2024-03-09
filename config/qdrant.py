from qdrant_client import QdrantClient

from constant.config import QDRANT_URL, QDRANT_INDEX_JOB_SEARCH, QDRANT_INDEX_RESUME_SEARCH

class QdrantVDB:
    QDRANT_URL = QDRANT_URL
    QDRANT_INDEX_JOB_SEARCH = QDRANT_INDEX_JOB_SEARCH
    QDRANT_INDEX_RESUME_SEARCH = QDRANT_INDEX_RESUME_SEARCH

    @staticmethod
    def setup_qdrant_connection() -> QdrantClient:
        return QdrantClient(QdrantVDB.QDRANT_URL)
