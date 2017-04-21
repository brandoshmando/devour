from devour import kafka
from devour import schemas


class BaseProducer(object):
    def __init__(self, *args, **kwargs):
        assert hasattr(self, 'ProducerConfig'), (
            '{0} requires ProducerConfig class to be declared.'.format(self.__class__.__name__)
        )

    def produce(self, context={}, extras={}):
        # get kafka related items
        topic = self.get_topic(context)
        partition_key = self.get_partition_key(context)
        producer_type = getattr(self.ProducerConfig,
                            'producer_type', 'simple_producer')
        p = kafka.get_producer(topic, producer_type)

        # build message
        schema_class = self.get_schema(context)
        message = self.get_message(context, schema_class, extras)

        # produce message to kafka
        p.produce(message, partition_key)

    def get_topic(self, context):
        """
        override this with custom logic
        to return desired topic name (str)
        based on event. should never return None
        """

        return getattr(self.ProducerConfig, 'topic', self._get_generic_topic())

    def get_schema(self, context):
        """
        override this with custom logic
        to return desired schema class
        based on event or topic. should never return None
        """

        schema_class = getattr(self.ProducerConfig, 'schema_class', None)
        return schema_class

    def get_partition_key(self, context):
        """
        avoid overriding with complex partitioning logic
        here. there should be a more efficient way for you
        to determine parition_key i.e. stored value
        """
        key = None
        if hasattr(self, 'partition_key'):
            key = getattr(self, 'partition_key')
        return key

    def get_message(self, context, schema_class, extras):
        """
        avoid overriding this method. if custom tweaks to
        message are needed, do so with schema logic
        """

        raise NotImplementedError('{0} must define a get_message method'.format(self.__class__.__name__))

    def _get_generic_topic(self, identifier='topic'):
        """
        attempts to create a generic topic if topic is not provided on
        ProducerConfig. topic__<class name>.
        """

        return '{0}__{1}'.format(identifier, self.__class__.__name__.lower())


class Producer(BaseProducer):
    def __init__(self, payload, *args, **kwargs):
        self.payload = payload
        super(Producer, self).__init__(*args, **kwargs)

    def get_message(self, context, schema_class, extras):
        """
        avoid overriding this method. if custom tweaks to
        message are needed, do so with schema logic
        """

        message_data = schema_class(data=self.payload, extras=extras).data
        return message_data

    def get_schema(self, context):
        schema_class = super(Producer, self).get_schema(context)
        return schema_class or schemas.Schema
