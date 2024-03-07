import os
from dotenv import load_dotenv
import uvicorn
from app.server import app
# from .worker.start_consumer import start_kafka_consumer

if __name__ == "__main__":
    # Load environment variables from .base.env
    load_dotenv(dotenv_path="./builders/.base.env")

    # Start worker
    # start_kafka_consumer()

    http_port = int(os.getenv("HTTP_PORT", 8080))

    # Start HTTP server
    uvicorn.run("app.server:app", host="127.0.0.1", port=http_port, reload=True)
