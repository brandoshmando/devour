import mock
from unittest import TestCase
from devour.handlers import ClientHandler
from devour.producers import _ProducerProxy
from threading import local

class TestClientHandler(TestCase):
    def setUp(self):
        self.config = {
            "hosts":"fakehost:fakeport",
            "ssl_config": None
        }

        conf = mock.MagicMock()
        conf.__getitem__.return_value = self.config
        self.settings = mock.MagicMock()
        type(self.settings).KAFKA_CONFIG = mock.PropertyMock(return_value=conf)

    def test_handler_init(self):
        handler = ClientHandler()

        self.assertTrue(isinstance(handler._client, local))
        self.assertTrue(isinstance(handler.producers, local))

        self.assertEqual(len(handler._client.__dict__.keys()), 0)
        self.assertEqual(len(handler.producers.__dict__.keys()), 0)

    @mock.patch('devour.handlers.load_module')
    @mock.patch('devour.handlers.pykafka.KafkaClient')
    def test_check_status(self, mocked_client, mocked_load):
        mocked_client.reset_mock()
        mocked_load.reset_mock()
        self.settings.reset_mock()

        mocked_load.return_value = self.settings

        handler = ClientHandler()

        # call twice
        handler._check_status()
        self.assertEqual(len(handler._client.__dict__.keys()), 1)

        handler._check_status()
        self.assertEqual(len(handler._client.__dict__.keys()), 1)

        self.assertTrue(handler._client, 'pykafka')
        mocked_client.assert_called_once_with(
            hosts='fakehost:fakeport',
            ssl_config=None,
            zookeeper_hosts=None
        )

    @mock.patch('devour.handlers.load_module')
    @mock.patch('devour.handlers.pykafka.KafkaClient')
    def test_get_topic(self, mocked_client, mocked_load):
        mocked_client.reset_mock()
        mocked_load.reset_mock()
        self.settings.reset_mock()

        config = {
            "hosts":"fakehost:fakeport",
            "ssl_config": None
        }

        mocked_load.return_value = self.settings

        mocked_topic = mock.MagicMock()
        mocked_client.return_value.topics.__getitem__.return_value = mocked_topic

        handler = ClientHandler()
        handler.get_topic('test')

        mocked_client.return_value.topics.__getitem__.assert_called_once_with('test')

    @mock.patch('devour.handlers.load_module')
    @mock.patch('devour.handlers.pykafka.KafkaClient')
    def test_get_producer_sync(self, mocked_client, mocked_load):
        mocked_client.reset_mock()
        mocked_load.reset_mock()
        self.settings.reset_mock()

        mocked_load.return_value = self.settings

        mocked_topic = mock.MagicMock()
        mocked_client.return_value.topics.__getitem__.return_value = mocked_topic

        handler = ClientHandler()
        prod = handler.get_producer('test')

        # first call sets
        self.assertTrue(isinstance(prod, _ProducerProxy))
        mocked_topic.get_sync_producer.assert_called_once()
        self.assertEqual(len(handler._client.__dict__.keys()), 1)
        self.assertTrue(hasattr(handler.producers, 'test__sync_producer'))

        # second call retrieves
        prod = handler.get_producer('test')

        self.assertTrue(isinstance(prod, _ProducerProxy))
        mocked_topic.get_sync_producer.assert_called_once()
        self.assertEqual(len(handler._client.__dict__.keys()), 1)
        self.assertTrue(hasattr(handler.producers, 'test__sync_producer'))

        # third call creates new
        prod = handler.get_producer('new')

        self.assertTrue(isinstance(prod, _ProducerProxy))
        self.assertEqual(len(mocked_topic.get_sync_producer.mock_calls), 2)
        self.assertEqual(len(handler.producers.__dict__.keys()), 2)
        self.assertTrue(hasattr(handler.producers, 'new__sync_producer'))

    @mock.patch('devour.handlers.load_module')
    @mock.patch('devour.handlers.pykafka.KafkaClient')
    def test_get_producer_async(self, mocked_client, mocked_load):
        mocked_client.reset_mock()
        mocked_load.reset_mock()
        self.settings.reset_mock()

        mocked_load.return_value = self.settings

        mocked_topic = mock.MagicMock()
        mocked_client.return_value.topics.__getitem__.return_value = mocked_topic

        handler = ClientHandler()
        prod = handler.get_producer('test', 'producer')

        # first call sets
        self.assertTrue(isinstance(prod, _ProducerProxy))
        mocked_topic.get_producer.assert_called_once()
        self.assertTrue(hasattr(handler.producers, 'test__producer'))

        # second call retrieves
        prod = handler.get_producer('test', 'producer')

        self.assertTrue(isinstance(prod, _ProducerProxy))
        mocked_topic.get_producer.assert_called_once()
        self.assertEqual(len(handler._client.__dict__.keys()), 1)
        self.assertTrue(hasattr(handler.producers, 'test__producer'))

        # third call creates new
        prod = handler.get_producer('new', 'producer')

        self.assertTrue(isinstance(prod, _ProducerProxy))
        self.assertEqual(len(mocked_topic.get_producer.mock_calls), 2)
        self.assertEqual(len(handler._client.__dict__.keys()), 1)
        self.assertEqual(len(handler.producers.__dict__.keys()), 2)
        self.assertTrue(hasattr(handler.producers, 'new__producer'))


    @mock.patch('devour.handlers.load_module')
    @mock.patch('devour.handlers.pykafka.KafkaClient')
    def test_get_consumer_simple(self, mocked_client, mocked_load):
        mocked_client.reset_mock()
        mocked_load.reset_mock()
        self.settings.reset_mock()

        mocked_load.return_value = self.settings

        mocked_topic = mock.MagicMock()
        mocked_client.return_value.topics.__getitem__.return_value = mocked_topic

        handler = ClientHandler()
        cons = handler.get_consumer('test', {'key': 'val'})

        mocked_topic.get_simple_consumer.assert_called_once_with(key='val')

    @mock.patch('devour.handlers.load_module')
    @mock.patch('devour.handlers.pykafka.KafkaClient')
    def test_get_consumer_simple(self, mocked_client, mocked_load):
        mocked_client.reset_mock()
        mocked_load.reset_mock()
        self.settings.reset_mock()

        mocked_load.return_value = self.settings

        mocked_topic = mock.MagicMock()
        mocked_client.return_value.topics.__getitem__.return_value = mocked_topic

        handler = ClientHandler()
        cons = handler.get_consumer('test', {'key': 'val'}, 'balanced_consumer')

        mocked_topic.get_balanced_consumer.assert_called_once_with(key='val')


    def test_stop_all_producers(self):
        producers = {
            'first': mock.MagicMock(),
            'second': mock.MagicMock(),
            'third': mock.MagicMock()
        }

        handler = ClientHandler()
        for k,v in producers.items():
            setattr(handler.producers, k, v)

        handler.stop_all_producers()

        for prod in handler.producers.__dict__.values():
            prod.stop.assert_called_once()
