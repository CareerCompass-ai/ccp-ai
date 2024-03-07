from threading import Thread
from kafka_consumer import KafkaConsumerWrapper

def start_kafka_consumer():
    consumer = KafkaConsumerWrapper(topic='your-topic') 

    def consume_messages():
        for message in consumer.consume():
            print("Received message:", message)

    consumer_thread = Thread(target=consume_messages, daemon=True)
    consumer_thread.start()
    
