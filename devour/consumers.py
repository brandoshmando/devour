import pykafka
import json
import logging
from devour import exceptions, schemas
from devour.utils.helpers import validate_config
from devour.handlers import ClientHandler, ProducerHandler

class DevourConsumer(object):

    def __init__(self):
        """
        :consumer_topic: - string name of topic to be consumed from
        :consumer_digest: - string name of the function used to manipulate kafka output
        :consumer_type: - type of pykafka consumer to use. simple_consumer or balanced_consumer
        :consumer_config: - dictionary containing all kwargs needed to config the consumer type. Any extras
        will be ignored

        :dump_json: - bool determines if consumer loads json message.value into consumer.digest()
        :dump_json: - bool determines if consumer dumps raw message.value into consumer.digest()
        :dump_obj: - bool determines if consumer dumps message object into consumer.digest()
        default behavior loads json representation of message.value and uses double star notation to
        dump result as kwargs to consumer.digest()
        """

        # required attrs
        self.client = ClientHandler()
        self.topic = getattr(self, 'consumer_topic', None)
        self.type = getattr(self, 'consumer_type', None)
        self.digest_name = getattr(self, 'consumer_digest', 'digest')
        self.digest = getattr(self, self.digest_name, None)
        self.config = getattr(self, 'consumer_config', {})

        required = [
            'topic',
            'type'
        ]

        for req in required:
            if not getattr(self, req, None):
                raise AttributeError("{0} must declare a consumer_{1} attrubute.".format(self.__class__.__name__, req))

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

    def configure(self, client_config):
        if self.config:
            self._validate_config(self.config, self.type)

        # setup log
        log_name = self.config.pop('log_name', __name__)
        self.logger = logging.getLogger(log_name)

        self.consumer = self.client.generate_consumer(self.topic, self.config, self.type)

        return True

    def consume(self):
        if self.consumer is None:
            raise exceptions.DevourConfigException('configure must be called before consume')

        # use _format_digest so all logic determining format is run
        # before consuming, preventing logic from running for each message
        formatted_digest = self._format_digest()
        for m in self.consumer:
            if m is not None:
                try:
                    formatted_digest(m)
                except Exception as e:
                    self.logger.exception("{0} Error".format(e.__class__.__name__))

    def _format_digest(self):
        # check options for digest before consuming
        # and return new function so that these checks
        # are not taking place for each message
        # TODO: custom serialization?
        if self.dump_json:
            formatted = lambda m: self.digest(json.loads(m.value))
        elif self.dump_raw:
            formatted = lambda m: self.digest(m.value)
        elif self.dump_obj:
            formatted = lambda m: self.digest(m)
        else:
            formatted = lambda m: self.digest(**json.loads(m.value))

        return formatted

    def _validate_config(self, config, consumer_type):
        try:
            schema = getattr(schemas, consumer_type.upper() + '_SCHEMA')
        except AttributeError:
            # this should never happen, but...
            raise exceptions.DevourConfigException('No schema for consumer type {0}'.format(consumer_type))

        return validate_config(schema, config)
