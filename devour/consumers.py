import pykafka
import json
from devour import exceptions

class DevourConsumer(object):

    def __init__(self, *args, **kwargs):
        """
        :consumer_topic: - string name of topic to be consumed from
        :consumer_digest: - string name of the function used to manipulate kafka output
        :consumer_type: - type of pykafka consumer to use. simple_consumer or balanced_consumer
        """

        # required attrs
        self.topic = getattr(self, 'consumer_topic', None)
        self.type = getattr(self, 'consumer_type', None)
        self.digest_name = getattr(self, 'consumer_digest', 'digest')
        self.digest = getattr(self, self.digest_name, None)

        required = [
            'topic',
            'type'
        ]

        for req in required:
            if not getattr(self, req, None):
                raise AttributeError("%s must declare a consumer_%s attrubute." % (self.__class__.__name__, req))

        if not callable(self.digest):
            raise NotImplementedError(
                '{0} must be a function on {1}'.format(self.digest_name, self.__class__.__name__)
            )

        # not required
        self.dump_json = getattr(self, 'dump_json', False)
        self.dump_raw = getattr(self, 'dump_raw', False)
        self.dump_obj = getattr(self, 'dump_obj', False)

        # internal
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
        except AttributeError:
            raise exceptions.DevourConfigException('consumer_topic %s not one of simple_consumer or balanced_consumer')

        return True

    def _consume(self):
        if self.consumer is None:
            raise exceptions.DevourConfigException('_configure must be called before _consume')

        # use format_digest so all logic determining format is run
        # before consuming, preventing logic from running for each message
        formatted_digest = self.format_digest()
        for m in self.consumer:
            if m is not None:
                formatted_digest(m)

    def format_digest(self):
        # check options for digest before consuming
        # and return new function so that these checks
        # are not taking place for each message
        # custom serialization?
        if self.dump_json:
            formatted = lambda m: self.digest(json.loads(m.value))
        elif self.dump_raw:
            formatted = lambda m: self.digest(m.value)
        elif self.dump_obj:
            formatted = lambda m: self.digest(m)
        else:
            formatted = lambda m: self.digest(**json.loads(m.value))

        return formatted
