from kafka import KafkaConsumer

class KafkaConsumerWrapper:
    def __init__(self, topic):
        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers='localhost:9092', 
            group_id='my-group',
            auto_offset_reset='earliest', 
            enable_auto_commit=True,
            auto_commit_interval_ms=1000, 
            value_deserializer=lambda x: x.decode('utf-8') 
        )

    def consume(self):
        for message in self.consumer:
            yield message.value

