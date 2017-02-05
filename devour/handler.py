import os
from pykafka import KafkaClient
from .exceptions import DevourConfigException
from .utils.helpers import validate_config
from .utils.loaders import load_module, load_consumer_class

class ClientHandler(object):
    def __init__(self, auto_start=True, *args, **kwargs):
        self.client = None
        self.topics = None

        if auto_start:
            self._configure()

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
            self.client = pykafka.KafkaClient(
                hosts=config.get('hosts'),
                zookeeper_hosts=config.get('zookeeper_hosts'),
                ssl_config=config.get('ssl_config')
            )

            self.topics = self.client.topics
        except AttributeError:
            raise exceptions.DevourConfigException('consumer_type {0} not one of simple_consumer or balanced_consumer'.format(self.type))
        except KeyError:
            raise exceptions.DevourConfigException('topic {0} does not exist on current kafka cluster'.format(self.topic))

        return True

    def _check_status(self):
        ok =  self.client and self.topics
        if not ok:
            raise DevourConfigException('Client not configured properly.')
        return True

    def generate_producer(topic, producer_type='sync_producer'):
        self._check_status()
        pass

    def generate_consumer(self, topic, config, consumer_type='simple_consumer'):
        self._check_status()

        try:
            consumer = getattr(topic, 'get_{0}'.format(self.type), None)(**config)
        except AttributeError:
            raise exceptions.DevourConfigException('consumer_type {0} not one of simple_consumer or balanced_consumer'.format(self.type))
        except KeyError:
            raise exceptions.DevourConfigException('topic {0} does not exist on current kafka cluster'.format(self.topic))
