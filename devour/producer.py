from . import _client

class DevourProducerFactory(object):
    def __init__(self, client, *args, **kwargs):
        super(DevourProducerFactory, self).__init__(*args, **kwargs)
        self.client = _client
        self.topics = _client.topics

    def manufacture(self, topic, producer_type='sync_producer'):
        try:
            prod = getattr(self.topics[topic], 'get_{0}'.format(producer_type))
        except AttributeError:
            #invalid producer_type
            raise
        except KeyError:
            #missing topic
            raise

        return prod
