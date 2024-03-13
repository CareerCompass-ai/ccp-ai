import os
from dotenv import load_dotenv

import config.config as cfg

dotenv_path = os.path.join(cfg.ROOT_FOLDER, "builders", ".base.env")
load_dotenv(dotenv_path=dotenv_path)

# Hosting server
SERVER_IP = os.getenv("SERVER_IP")
PG_PORT = os.getenv("PG_PORT")
KAFKA_PORT = os.getenv("KAFKA_PORT")
QDRANT_PORT = os.getenv("QDRANT_PORT")

# HTTP server
HTTP_PORT = os.getenv("HTTP_PORT")

# postgres
DATABASE_URL = os.getenv("DATABASE_URL")

# qdrant
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_INDEX_JOB_SEARCH = os.getenv("QDRANT_INDEX_JOB_SEARCH") 
QDRANT_INDEX_RESUME_SEARCH = os.getenv("QDRANT_INDEX_RESUME_SEARCH") 

