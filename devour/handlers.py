import os
import pykafka
import atexit
from threading import local
from devour.exceptions import DevourConfigException
from devour.utils.helpers import validate_config
from devour.utils.loaders import load_module, load_consumer_class
from devour.validators import  CONFIG_VALIDATOR
from devour.proxies import _ProducerProxy


class ClientHandler(object):
    def __init__(self, *args, **kwargs):
        self._client = local()
        self.producers = local()

        # register exit callback
        # this ensures all producers
        # push all messages from it's internal
        # queue it shuts down, thus preventing
        # data loss
        atexit.register(self.stop_all_producers)

    def _configure(self):
        settings_path = os.environ.get('KAFKA_SETTINGS_PATH') or \
                        'settings'
        settings = load_module(settings_path)

        try:
            kafka = getattr(settings, 'KAFKA_CONFIG')
            config = kafka['client']
        except AttributeError:
            raise DevourConfigException(
                'missing KAFKA_CONFIG in settings.'
            )
        except KeyError:
            raise DevourConfigException(
                'missing client settings in KAFKA_CONFIG'
            )

        #validate congiuration args
        validate_config(CONFIG_VALIDATOR, config)

        # setup ssl if provided
        ssl = None
        if config.get('ssl_config'):
            ssl = pykafka.SslConfig(**config['ssl_config'])

        # attempt to connect to kafka cluster
        # set manually since pykafka is the only
        # lib we support for now
        self._client.pykafka = pykafka.KafkaClient(
            hosts=config.get('hosts'),
            zookeeper_hosts=config.get('zookeeper_hosts'),
            ssl_config=ssl
        )
        return True

    def _check_status(self):
        if not hasattr(self._client, 'pykafka'):
            self._configure()
        return True

    def get_topic(self, key):
        self._check_status()
        try:
            return self._client.pykafka.topics[bytes(key)]
        except KeyError:
            raise DevourConfigException('topic {0} does not exist on current kafka cluster'.format(key))

    def get_producer(self, topic_name, producer_type='sync_producer'):
        self._check_status()
        formatted = '{0}__{1}'.format(topic_name, producer_type)

        if hasattr(self.producers, formatted):
            return _ProducerProxy(getattr(self.producers, formatted))

        topic = self.get_topic(topic_name)
        try:
            producer = getattr(topic, 'get_' + producer_type)() # need to pass in kwargs here
        except AttributeError:
            raise DevourConfigException('producer_type {0} not one of sync_producer_consumer or produce'.format(producer_type))

        # persist the producer
        setattr(self.producers, formatted, producer)
        return _ProducerProxy(producer)

    def get_consumer(self, topic_name, config, consumer_type='simple_consumer'):
        self._check_status()
        topic = self.get_topic(topic_name)

        try:
            consumer = getattr(topic, 'get_{0}'.format(consumer_type))(**config)
        except AttributeError:
            raise DevourConfigException('consumer_type {0} not one of simple_consumer or balanced_consumer'.format(self.consumer_type))

        return consumer

    def stop_all_producers(self):
        for prod in self.producers.__dict__.keys():
            getattr(self.producers, prod).stop()
