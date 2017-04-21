from devour.producers import Producer
from example.schemas import GenericSimpleMessageSchema

class GenericSimpleMessage(Producer):
    class ProducerConfig:
        topic = 'test'
        schema_class = GenericSimpleMessageSchema
        producer_type = 'sync_producer'
