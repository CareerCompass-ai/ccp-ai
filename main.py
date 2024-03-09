import uvicorn
from app.server import app
# from .worker.start_consumer import start_kafka_consumer

from constant.config import HTTP_PORT

if __name__ == "__main__":
    # Load env

    # Start worker
    # start_kafka_consumer()

    # Start HTTP server
    uvicorn.run("app.server:app", host="127.0.0.1", port=int(HTTP_PORT), reload=True)
