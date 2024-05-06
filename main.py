import threading
import uvicorn
from app.server import app
from worker.start_consumer import start_kafka_consumer
import constant.config as cfg

if __name__ == "__main__":
    # def start_consumer():
    #     start_kafka_consumer()

    # # Create a thread for Kafka consumer and set it as a daemon thread
    # consumer_thread = threading.Thread(target=start_consumer, daemon=True)

    # Start the Kafka consumer thread
    # consumer_thread.start()

    # Start HTTP server in the main thread
    uvicorn.run("app.server:app", host="127.0.0.1", port=int(cfg.HTTP_PORT), reload=True)
