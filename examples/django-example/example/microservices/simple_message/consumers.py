from devour.consumers import DevourConsumer
from example.microservices.config import SIMPLE_CONSUMER_CONFIG
from .schemas import SimpleMessageConsumerSchema

class SimpleMessageConsumer(DevourConsumer):
    consumer_type = 'simple_consumer'
    topic = 'test'
    config = SIMPLE_CONSUMER_CONFIG
    schema_class = SimpleMessageConsumerSchema

    def digest(self, offset, message):
        print message
