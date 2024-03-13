from confluent_kafka import Consumer, KafkaError, KafkaException
from app.usecases.sync_qdrant import SyncUsecase
import json

import constant.config as cfg

class KafkaConsumerWrapper:
    def __init__(self, topics):
        conf = {
            'bootstrap.servers': f'{cfg.SERVER_IP}:{cfg.KAFKA_PORT}',
            'group.id': 'my_consumer_group',        
            'auto.offset.reset': 'earliest'      
        }
        self.consumer = Consumer(conf)
        self.consumer.subscribe(topics)
    
    #Handle_topic 
    def handle_topic_job(self, msg):
        # SyncUsecase(msg.value())
        data = json.loads(msg.key())
        id = data.get('id')
        print(id)
        #CODE HERE!
    def handle_topic_resume(self, msg):
        print('TABLE RESUME')
        #CODE HERE!

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
                    elif msg.topic() == 'table_resume.public.resume':
                        self.handle_topic_resume(msg)
        except KeyboardInterrupt:
            pass

        finally:
            self.consumer.close()

