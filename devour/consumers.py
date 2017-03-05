try:
    import ujson as json
except ImportError:
    import json
import pykafka
import logging
from devour.handlers import ClientHandler
from devour import exceptions, validators
from devour.utils.helpers import validate_config

class DevourConsumer(object):

    def __init__(self, auto_start=True):
        """
        :consumer_topic: - string name of topic to be consumed from
        :consumer_digest: - string name of the function used to manipulate kafka output, defaults to 'digest'
        :consumer_type: - type of pykafka consumer to use. simple_consumer or balanced_consumer
        :consumer_config: - dictionary containing all kwargs needed to config the consumer type. Any extras
        will be ignored

        :dump_json: - bool determines if consumer loads json message.value into consumer.digest()
        :dump_raw: - bool determines if consumer dumps raw message.value into consumer.digest()
        :dump_obj: - bool determines if consumer dumps message object into consumer.digest()
        default behavior loads json representation of message.value and uses double star notation to
        dump result as kwargs to consumer.digest()
        """

        # required attrs
        self.topic = getattr(self, 'topic', None)
        self.type = getattr(self, 'consumer_type', None)
        self.digest_name = getattr(self, 'digest_name', 'digest')
        self.config = getattr(self, 'config', {})
        self.schema_class = getattr(self, 'schema_class', None)

        # not required
        self.dump_raw = getattr(self, 'dump_raw', False)
        self.dump_obj = getattr(self, 'dump_obj', False)
        self.dump_json = getattr(self, 'dump_json', False)

        required = [
            'topic',
            'type',
            'schema_class'
        ]

        for req in required:
            if not getattr(self, req, None):
                if not self.dump_json and (self.dump_raw or self.dump_obj) and req == 'schema_class':
                    continue
                raise AttributeError("{0} must declare a consumer_{1} attrubute.".format(self.__class__.__name__, req))

        if not callable(getattr(self, self.digest_name, None)):
            raise NotImplementedError(
                '{0} must be a function on {1}'.format(self.digest_name, self.__class__.__name__)
            )

        # internal
        self.client = None
        self.consumer = None

        if auto_start:
            self.configure()

    def configure(self):
        if self.config:
            validate_config(getattr(validators, self.type.upper() + '_VALIDATOR'), self.config)

        # setup log
        log_name = self.config.pop('log_name', __name__)
        self.logger = logging.getLogger(log_name)

        self.client = ClientHandler()
        self.consumer = self.client.get_consumer(self.topic, self.config, self.type)

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
        digest = getattr(self, self.digest_name)

        if self.dump_raw:
            formatted = lambda m: digest(m.offset, m.value)
        elif self.dump_obj:
            formatted = lambda m: digest(m.offset, m)
        else:
            formatted = lambda m: digest(
                m.offset,
                **self.schema_class(json.loads(m.value)).data
            )

        return formatted
