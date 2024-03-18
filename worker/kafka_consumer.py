from confluent_kafka import Consumer, KafkaError, KafkaException
from app.usecases.sync_qdrant import SyncUsecase
import json
class KafkaConsumerWrapper:
    def __init__(self, topics):

        # conf = {
        #     'bootstrap.servers': "157.245.50.16:9092",  #  Kafka brokers
        #     'group.id': 'my_consumer_group',        
        #     'auto.offset.reset': 'earliest'      
        # }
        self.consumer = Consumer({
            'bootstrap.servers': "157.245.50.16:9092",  #  Kafka brokers
            'group.id': 'my_consumer_group',        
            'auto.offset.reset': 'earliest'      
        })
        self.consumer.subscribe(topics)
        self.sync = SyncUsecase()
    #Handle_topic 
    def handle_topic_job(self, msg):
        # SyncUsecase(msg.value())
        data = json.loads(msg.key())
        id = data.get('id')
        print(id)
        #CODE HERE!
    def handle_topic_resume(self, msg):
        resume_id = json.loads(msg.key()).get('payload').get('id')
        self.sync.sync_resume_to_qdrant(resume_id)


    def consume(self):
        try:
            while True:
                msg = self.consumer.poll(timeout=1.0)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        # End of partition
                        print('%% %s [%d] reached end at offset %d\n' % (msg.topic(), msg.partition(), msg.offset()))
                    elif msg.error():
                        raise KafkaException(msg.error())
                else:
                    # Process message based in topic
                    if msg.topic() == 'cdc.public.ccp_job':
                        self.handle_topic_job(msg)
                    elif msg.topic() == 'cdc.public.ccp_resume':
                        self.handle_topic_resume(msg)
        except KeyboardInterrupt:
            pass

        finally:
            self.consumer.close()

