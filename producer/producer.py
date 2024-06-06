import json

from confluent_kafka import Producer

import constant.config as cfg
from pkg.logging import logger


class KafkaProducer:
    def __init__(self):
        conf = {
            'bootstrap.servers': f'{cfg.SERVER_IP}:{cfg.KAFKA_PORT}',
        }
        self.producer = Producer(conf)

    def produce_message(self, topic_name: str, payload: dict):
        """
        Produce a message to a Kafka topic.

        Parameters:
        - topic_name (str): The name of the Kafka topic.
        - payload (dict): The message payload to be sent.
        """
        try:
            self.producer.produce(topic_name, json.dumps(payload))
            self.producer.flush()
        except Exception as e:
            logger.error(f"Failed to produce message: {e}")
