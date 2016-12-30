import pykafka
import json
from devour import exceptions, schemas

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
        if self.config:
            self._validate_config(self.config, self.type)

        try:
            #attempt to connect to kafka cluster
            client = pykafka.KafkaClient(
                hosts=client_config.get('hosts'),
                zookeeper_hosts=client_config.get('zookeeper_hosts'),
                ssl_config=client_config.get('ssl_config')
            )

            #attempt to get topic
            topic = client.topics[self.topic]
            self.consumer = getattr(topic, 'get_{0}'.format(self.type), None)(**self.config)
        except AttributeError:
            raise exceptions.DevourConfigException('consumer_topic %s not one of simple_consumer or balanced_consumer' % self.type)
        except KeyError:
            raise exceptions.DevourConfigException('topic %s does not exist on current kafka cluster' % self.topic)

        return True

    def _validate_config(self, config, consumer_type):
        try:
            schema = getattr(schemas, consumer_type.upper() + '_SCHEMA')
        except AttributeError:
            # this should never happen, but...
            raise exceptions.DevourConfigException('No schema for consumer type %s' % consumer_type)

        for attr,req in schema.items():
            value = config.get(attr)
            if value:
                if not isinstance(value, req['type']):
                    raise exceptions.DevourConsumerException('%s is not of type %s' % (attr, req['type'].__name__))

                if req.get('dependents'):
                    for dep in req['dependents']:
                        if not config.get(dep):
                            raise exceptions.DevourConsumerException('%s requires %s atrribute to be set' % (attr, dep))
            else:
                if req['required']:
                    raise exceptions.DevourConsumerException('value for %s is required in consumer_config' % attr)

        return True

    def _consume(self):
        if self.consumer is None:
            raise exceptions.DevourConfigException('_configure must be called before _consume')

        # use _format_digest so all logic determining format is run
        # before consuming, preventing logic from running for each message
        formatted_digest = self._format_digest()
        for m in self.consumer:
            if m is not None:
                try:
                    formatted_digest(m)
                except:
                    #TODO handle/log exceptions
                    pass

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
