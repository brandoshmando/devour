from devour.consumers import DevourConsumer
from example.microservices.config import SIMPLE_MESSAGE_CONSUMER
from .schemas import SimpleMessageConsumerSchema

class SimpleMessageConsumer(DevourConsumer):
    consumer_type = 'simple_consumer'
    topic = 'test'
    config = SIMPLE_MESSAGE_CONSUMER
    schema_class = SimpleMessageConsumerSchema

    def digest(self, offset, message):
        print message
