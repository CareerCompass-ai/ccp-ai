import os
import yaml

from config.config import ROOT_FOLDER

from .kafka_consumer import KafkaConsumerWrapper

def load_topics_from_config():
    config_path = os.path.join(ROOT_FOLDER, 'builders', 'config.yaml')
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
        return config.get('topics', [])

def start_kafka_consumer():
    topics = load_topics_from_config()
    consumer = KafkaConsumerWrapper(topics)

    consumer.consume()

