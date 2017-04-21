try:
    import ujson as json
except ImportError:
    import json

class _ProducerProxy(object):
    """
    Proxy that ensures json.dumps is called on message before producing
    TODO: Allow pickling
    """
    def __init__(self, producer):
        self._producer = producer

    def produce(self, payload, partition_key=None):
        self._producer.produce(json.dumps(payload), partition_key)
