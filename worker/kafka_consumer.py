from confluent_kafka import Consumer, KafkaError, KafkaException
from app.usecases.sync_qdrant import SyncUsecase
import json

import constant.config as cfg


class KafkaConsumerWrapper:
    def __init__(self, topics):
        conf = {
            'bootstrap.servers': f'{cfg.SERVER_IP}:{cfg.KAFKA_PORT}',
            'group.id': 'my_consumer_group',        
            'auto.offset.reset': 'earliest',
            'debug': 'broker'
        }
        self.consumer = Consumer(conf)
        self.consumer.subscribe(topics)
        self.sync = SyncUsecase()

    def handle_topic_job(self, msg):
        print('TABLE JOB')
        data = json.loads(msg.key())
        id = data['payload'].get('id')
        print(id)

        self.sync.sync_job_to_qdrant_and_es(id)

    def handle_topic_resume(self, msg):
        resume_id = json.loads(msg.key()).get('payload').get('id')
        self.sync.sync_resume_to_qdrant(resume_id)

    def handle_topic_application(self, msg):
        print('ALO')
        resume_id = json.loads(msg.key()).get('payload').get('resume_id')
        self.sync.sync_jobs_applied_resume_to_qdrant(resume_id)
        
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
                    if msg.topic() == cfg.KAFKA_TOPIC_CDC_JOB:
                        self.handle_topic_job(msg)
                    elif msg.topic() == cfg.KAFKA_TOPIC_CDC_RESUME:
                        self.handle_topic_resume(msg)
                    elif msg.topic() == cfg.KAFKA_TOPIC_CDC_APPLICATION:
                        self.handle_topic_application(msg)
        except KeyboardInterrupt:
            pass

        finally:
            self.consumer.close()

