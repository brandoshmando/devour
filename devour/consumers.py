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
        :topic: - string name of topic to be consumed from
        :digest_name: - string name of the function used to manipulate kafka output, defaults to 'digest'
        :consumer_type: - type of pykafka consumer to use. simple_consumer or balanced_consumer
        :config: - dictionary containing all kwargs needed to config the consumer type. Any extras
        will be ignored
        :schema_class: - Schema class used to extract data from messages. Only required when
        using dump_json

        :dump_json: - bool determines if consumer loads json message.value into consumer.digest()
        :dump_raw: - bool determines if consumer dumps raw message.value into consumer.digest()
        :dump_obj: - bool determines if consumer dumps message object into consumer.digest()
        default behavior loads json representation of message.value and uses double star notation to
        dump result as kwargs to consumer.digest()
        """

        # not required
        self.dump_raw = getattr(self, 'dump_raw', False)
        self.dump_obj = getattr(self, 'dump_obj', False)
        self.dump_json = getattr(self, 'dump_json', False)

        # required attrs
        validation_message = '{0} requires {1} to be declared'

        assert hasattr(self, 'topic'), (
            validation_message.format(self.__class__.__name__, 'topic')

        )
        assert hasattr(self, 'consumer_type'), (
            validation_message.format(self.__class__.__name__, 'consumer_type')
        )
        # only if dump_json
        if not (self.dump_raw or self.dump_obj) and self.dump_json:
            assert hasattr(self, 'schema_class'), (
                validation_message.format(self.__class__.__name__, 'schema_class')
            )

        #ensure defaults
        self.digest_name = getattr(self, 'digest_name', 'digest')
        self.config = getattr(self, 'config', {})

        validate_config(getattr(validators, self.consumer_type.upper() + '_VALIDATOR'), self.config)

        # internal
        self.client = None
        self.consumer = None

        if auto_start:
            self.client = ClientHandler()
            self.consumer = self.client.get_consumer(self.topic, self.config, self.consumer_type)

    def consume(self):
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
            if hasattr(self, schema_class):
                formatted = lambda m: digest(
                    m.offset,
                    **self.schema_class(json.loads(m.value)).data
                )
            else:
                formatted = lambda m: digest(m.offset, json.loads(m.value))

        return formatted

    def digest(self, offset, *args, **kwargs):
        raise NotImplementedError(
            'digest method not implemented on {0}'.format(self.__class__.__name__))
