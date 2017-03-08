from devour import kafka


class BaseProducer(object):
    def __init__(self, payload, *args, **kwargs):
        assert hasattr(self, 'ProducerConfig'), (
            '{0} requires ProducerConfig class to be declared.'.format(self.__class__.__name__)
        )

        self.payload = payload
        super(BaseProducer, self).__init__(*args, **kwargs)

    def produce(self, event=None, produce_extras=None):
        raise NotImplementedError('produce() method not implemented')

    def get_topic(self, event):
        raise NotImplementedError('get_topic() method not implemented')

    def get_source(self, event, topic):
        raise NotImplementedError('get_source() method not implemented')

    def get_schema(self, event, topic):
        raise NotImplementedError('get_schema() method not implemented')

    def get_partition_key(self, event, topic):
        raise NotImplementedError('get_schema() method not implemented')

    def get_message(self, event, topic, produce_extras=None):
        raise NotImplementedError('get_message() method not implemented')


class GenericProducer(BaseProducer):

    def produce(self, event, produce_extras=None):
        topic = self.get_topic(event)
        source = self.get_source(event, topic)
        schema_class = self.get_schema(event, topic)
        partition_key = self.get_partition_key(event, topic)
        message = self.get_message(produce_extras)

        p = kafka.get_producer(topic, self.ProducerConfig.producer_type)
        p.produce(message, partition_key)

    def get_topic(self, event):
        """
        override this with custom logic
        to return desired topic name (str)
        based on event. should never return None
        """

        return getattr(self.ProducerConfig, 'topic', self._get_generic_topic())

    def get_source(self, event, topic):
        """
        defaults to lowered class name. this
        value is provided to the schema and is
        popped into the message for use in consumer logic.
        customize as you need
        """
        return self.__class__.__name__.lower()

    def get_schema(self, event, topic):
        """
        override this with custom logic
        to return desired schema class
        based on event or topic. should never return None
        """

        schema_class = getattr(self, 'schema_class', None)
        return schema_class

    def get_partition_key(self, event, topic):
        """
        avoid overriding with complex partitioning logic
        here. there should be a more efficient way for you
        to determine parition_key i.e. stored value
        """
        key = None
        if hasattr(self, topic +'_partition_key'):
            key = getattr(self, attr)
        elif hasattr(self, event +'_partition_key'):
            key = getattr(self, attr)
        elif hasattr(self, 'partition_key'):
            key = getattr(self, 'partition_key')

        return key

    def get_message(self, event, topic, produce_extras=None):
        """
        avoid overriding this method. if custom tweaks to
        message are needed, do so with schema logic
        """

        source = self.get_source(event, topic)
        schema_class = self.get_schema(event, topic)

        if schema_class:
            message_data = schema_class(
                data=self.payload,
                produce_extras=produce_extras
            ).data
        else:
            message_data = self.payload.copy().update(produce_extras)

        return message_data

    def _get_generic_topic(self, identifier='topic'):
        """
        attempts to create a generic topic if topic is not provided on
        ProducerConfig. based on app name and class name.
        """

        return '{0}__{1}'.format(identifier, self.__class__.__name__.lower())
