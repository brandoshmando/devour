import os
import pykafka
from threading import local
from .exceptions import DevourConfigException
from .utils.helpers import validate_config
from .utils.loaders import load_module, load_consumer_class
from devour.bin.schemas import  CONFIG_SCHEMA


class TopicWrapper(object):
    def __init__(self, client, *args, **kwargs):
        self._client = client

    def __getitem__(self, key):
        return self._client.topics[key]

    def __setitem__(self, key, value):
        self._client.topics[key] = value


class ProducerHandler(object):
    def __init__(self, client, *args, **kwargs):
        self._client = client
        self._topics = client.topics
        self._producers = local()

    def __getitem__(self, tup):
        key = tup[0]
        producer_type = tup[1]

        if hasattr(self._producers, key):
            return getattr(self._producers, key)

        prod = self._client.generate_producer(key, producer_type)
        setattr(self._producers, key, prod)
        return prod

    def __setitem__(self, key, value):
        if hasattr(self._producers, key):
            getattr(self._producers, key).stop()

        setattr(self._producers, key, value)

    def stop_all(self):
        for prod in self._producers.__dict__.keys():
            getattr(self._producers, prod).stop()


class ClientHandler(object):
    def __init__(self, auto_start=True, *args, **kwargs):
        self._client = local()
        self.topics = None
        self.producers = None

        if auto_start:
            self._configure()

    def __getitem__(self, key):
        if hasattr(self._client, key):
            return getattr(self._client, key)

        raise KeyError('ClientHandler not configured properly. Be sure to call _configure before accessing this client.')

    def __setitem__(self, key, value):
        if hasattr(self._client, key):
            self.producers.stop_all()
            del self._client.__dict__[key]

        setattr(self._client, key, value)

    def _configure(self, config_overrides={}):
        settings_path = os.environ.get('DEVOUR_SETTINGS') or 'settings'
        settings = load_module(settings_path)

        try:
            routes = getattr(settings, 'DEVOUR_ROUTES')
            config = getattr(settings, 'DEVOUR_CONFIG')
        except AttributeError:
            if routes:
                desc = 'DEVOUR_CONFIG'
            else:
                desc = 'DEVOUR_ROUTES'
            raise exceptions.DevourConfigException(
                'missing setting {0} in {1}.'.format(desc, os.basename(settings.__file__)))

        #validate congiuration args
        validate_config(CONFIG_SCHEMA, config)

        try:
            #attempt to connect to kafka cluster
            # set manually since pykafka is the only
            # lib we support for now
            self._client.pykafka = pykafka.KafkaClient(
                hosts=config.get('hosts'),
                zookeeper_hosts=config.get('zookeeper_hosts'),
                ssl_config=config.get('ssl_config')
            )
            self.topics = TopicWrapper(self._client.pykafka)
            self.producers = ProducerHandler(self._client.pykafka)

        except AttributeError:
            raise exceptions.DevourConfigException('consumer_type {0} not one of simple_consumer or balanced_consumer'.format(self.type))
        except KeyError:
            raise exceptions.DevourConfigException('topic {0} does not exist on current kafka cluster'.format(self.topic))
        return True

    def _check_status(self):
        ok =  hasattr(self._client, 'pykafka') or False
        if not ok:
            raise DevourConfigException('Kafka Client not configured properly.')
        return True

    def get_topic(self, key):
        self._check_status()
        return self._client.pykafka.topics[key]

    def generate_producer(topic, producer_type='sync_producer'):
        self._check_status()
        pass

    def generate_consumer(self, topic_name, config, consumer_type='simple_consumer'):
        self._check_status()
        topic = self.topics[topic_name]

        try:
            consumer = getattr(topic, 'get_{0}'.format(consumer_type), None)(**config)
        except AttributeError:
            raise exceptions.DevourConfigException('consumer_type {0} not one of simple_consumer or balanced_consumer'.format(self.type))
        except KeyError:
            raise exceptions.DevourConfigException('topic {0} does not exist on current kafka cluster'.format(self.topic))

        return consumer
