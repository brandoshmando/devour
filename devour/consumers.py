import pykafka

class DevourConsumer(object):

    def __init__(self, *args, **kwargs):
        """
        :consumer_topic: - string name of topic to be consumed from
        :consumer_digest: - string name of the function used to manipulate kafka output
        :consumer_type: - type of pykafka consumer to use. simple_consumer or balanced_consumer
        """

        required = [
            'topic',
            'type'
        ]

        self.topic = getattr(self, 'consumer_topic', None)
        self.type = getattr(self, 'consumer_type', None)
        self.digest_name = getattr(self, 'consumer_digest', None) or 'digest'

        for req in required:
            if not getattr(self, req, None):
                raise AttributeError("%s must declare a consumer_%s attrubute." % (self.__class__.__name__, req))

        self.consumer = None

    def _configure(self, client_config):
        try:
            #attempt to connect to kafka cluster
            client = pykafka.KafkaClient(
                hosts=client_config.get('hosts'),
                ssl_config=client_config.get('ssl_config')
            )

            #attempt to get topic
            topic = client.topics[self.topic]

            self.consumer = getattr(topic, 'get_{0}'.format(self.type), None)()
        except Exception, e:
            raise e

        return True

    def _consume(self):
        #check configured has been called (self.consumer not None)
        #and check for digest implementation here
        # begin loop and pass messages into digest
        for m in self.consumer:
            if m is not None:
                getattr(self, self.get_digest(), None)(m.value)

    def get_digest(self):
        # overwritable if extra logic is needed.  must return str
        # name of function to be used in self._consume()
        return self.digest_name
