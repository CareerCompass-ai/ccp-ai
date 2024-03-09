import os
from dotenv import load_dotenv
from config.config import ROOT_FOLDER

dotenv_path = os.path.join(ROOT_FOLDER, "builders", ".base.env")
load_dotenv(dotenv_path=dotenv_path)

# HTTP server
HTTP_PORT = os.getenv("HTTP_PORT")

# postgres
DATABASE_URL = os.getenv("DATABASE_URL")

# qdrant
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_INDEX_JOB_SEARCH = os.getenv("QDRANT_INDEX_JOB_SEARCH") 
QDRANT_INDEX_RESUME_SEARCH = os.getenv("QDRANT_INDEX_RESUME_SEARCH") 
