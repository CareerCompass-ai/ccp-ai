import os
from dotenv import load_dotenv

import config.config as cfg

dotenv_path = os.path.join(cfg.ROOT_FOLDER, "builders", ".base.env")
load_dotenv(dotenv_path=dotenv_path)

# Hosting server
SERVER_IP = os.getenv("SERVER_IP")
KAFKA_SERVER_IP = os.getenv("KAFKA_SERVER_IP")
DB_SERVER_IP = os.getenv("DB_SERVER_IP")
ES_SERVER_IP = os.getenv("ES_SERVER_IP")

PG_PORT = os.getenv("PG_PORT")
KAFKA_PORT = os.getenv("KAFKA_PORT")
QDRANT_PORT = os.getenv("QDRANT_PORT")
WEAVIATE_PORT=os.getenv("WEAVIATE_PORT")
MINIO_PORT = os.getenv("MINIO_PORT")
ES_PORT = os.getenv("ES_PORT")

# HTTP server
HTTP_PORT = os.getenv("HTTP_PORT")
HTTP_ADMIN_USER_NAME = os.getenv("HTTP_ADMIN_USER_NAME")
HTTP_ADMIN_PASSWORD = os.getenv("HTTP_ADMIN_PASSWORD")

# postgres
DATABASE_URL = os.getenv("DATABASE_URL")

# qdrant
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_INDEX_JOB_SEARCH = os.getenv("QDRANT_INDEX_JOB_SEARCH") 
QDRANT_INDEX_RESUME_SEARCH = os.getenv("QDRANT_INDEX_RESUME_SEARCH")

# weaviate
WEAVIATE_URL=os.getenv("WEAVIATE_URL")
WEAVIATE_API_KEY=os.getenv("WEAVIATE_API_KEY")

# es
ES_URL = os.getenv("ES_URL")
ES_USERNAME = os.getenv("ES_USERNAME")
ES_PASSWORD = os.getenv("ES_PASSWORD")
ES_INDEX_JOB_SEARCH = os.getenv("ES_INDEX_JOB_SEARCH") 
ES_INDEX_RESUME_SEARCH = os.getenv("ES_INDEX_RESUME_SEARCH") 


# kafka
KAFKA_TOPIC_CDC_JOB = os.getenv("KAFKA_TOPIC_CDC_JOB")
KAFKA_TOPIC_CDC_RESUME = os.getenv("KAFKA_TOPIC_CDC_RESUME")
KAFKA_TOPIC_CDC_APPLICATION = os.getenv("KAFKA_TOPIC_CDC_APPLICATION")

#minio
MINIO_URL = os.getenv("MINIO_URL")
MINIO_USERNAME = os.getenv("MINIO_USERNAME")
MINIO_PASSWORD = os.getenv("MINIO_PASSWORD")
MINIO_BUCKET_JOB = os.getenv("MINIO_BUCKET_JOB")
MINIO_BUCKET_RESUME = os.getenv("MINIO_BUCKET_RESUME")