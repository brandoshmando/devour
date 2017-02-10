try:
    import ujson as json
except ImportError:
    import json
import mock
from unittest import TestCase
from devour.handlers import _ProducerProxy


class TestProducerProxy(TestCase):
    def test_produce_called_with_proper_args(self):
        producer = mock.MagicMock()
        proxy = _ProducerProxy(producer)

        proxy.produce('message', 'partition_key')
        producer.produce.assert_called_once_with(json.dumps('message'), 'partition_key')
