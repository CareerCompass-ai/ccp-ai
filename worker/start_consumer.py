from threading import Thread
from .kafka_consumer import KafkaConsumerWrapper

def start_kafka_consumer():
    #List of topics
    topics = ['cdc.public.ccp_job', 'cdc.public.ccp_resume']
    consumer = KafkaConsumerWrapper(topics) 

    # def consume_messages():
    consumer.consume()
        # for message in consumer.consume():
        #     print("Received message:", message)

    # consumer_thread = Thread(target=consume_messages, daemon=True)
    # consumer_thread.start()
    
