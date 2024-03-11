from confluent_kafka import Consumer, KafkaError, KafkaException
import json
class KafkaConsumerWrapper:
    def __init__(self, topic):
        conf = {
            'bootstrap.servers': 'localhost:9092',  #  Kafka brokers
            'group.id': 'my_consumer_group',        
            'auto.offset.reset': 'earliest'      
        }
        self.consumer = Consumer(conf)
        self.consumer.subscribe([topic])
    def consume(self):
        try:
            while True:
                msg = self.consumer.poll(timeout=1.0)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        # End of partition
                        print('%% %s [%d] reached end at offset %d\n' %
                            (msg.topic(), msg.partition(), msg.offset()))
                    elif msg.error():
                        raise KafkaException(msg.error())
                else:
                    # Process message
                    try:
                        data = json.loads(msg.value())
                        payload = data.get('payload')
                        if payload:
                            before = payload.get('before')
                            after = payload.get('after')
                            if before is None and after is not None:
                                print(payload)
                            elif before is not None and after is not None:
                                print('update')
                            elif before is not None and after is None:
                                print('delete')
                            else:
                                print('Unknown operation')
                        else:
                            print('Payload missing or invalid format:', data)
                    except Exception as e:
                        print('Error processing message:', e)
                        # Handle the error as per your requirement
        except KeyboardInterrupt:
            pass

        finally:
            self.consumer.close()

