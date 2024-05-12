import os
from dotenv import load_dotenv

import config.config as cfg

dotenv_path = os.path.join(cfg.ROOT_FOLDER, "builders", ".base.env")

load_dotenv(dotenv_path=dotenv_path)

OPENAI_API_KEY = str(os.getenv("OPENAI_KEY"))
OPENAI_EMBEDDING_MODEL = (str(os.getenv("OPENAI_EMBEDDING_MODEL")))
OPENAI_COMPLETION_MODEL = (str(os.getenv("OPENAI_COMPLETION_MODEL")))
SUMMARIZE_JOB_DESCRIPTION_PROMPT = (str(os.getenv("SUMMARIZE_JOB_DESCRIPTION_PROMPT")))
SUMMARIZE_RESUME_PROMPT = (str(os.getenv("SUMMARIZE_RESUME_PROMPT")))
COMMON_JOB_TITLE_PROMPT = (str(os.getenv("COMMON_JOB_TITLE_PROMPT")))
