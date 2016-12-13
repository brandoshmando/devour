import mock
from unittest import TestCase
from devour import exceptions
from test_utils import DevourTestMixin

class TestSimpleConsumer(TestCase, DevourTestMixin):
    def setUp(self):
        self.success = self.generate_subclass(
            {
                'consumer_topic':'topic',
                'consumer_type':'simple_consumer'
            },
            {
                'digest': mock.MagicMock()
            }
        )

        self.failure_one = self.generate_subclass(
            {'consumer_type': 'simple_consumer'}
        )

        self.failure_two = self.generate_subclass(
            {'consumer_topic': 'topic'}
        )

        self.digest = mock.MagicMock()

        self.cls = self.generate_subclass(
            {
                'consumer_topic':'topic',
                'consumer_type':'simple_consumer'
            },
            {
                'digest': self.digest
            }
        )()


    def test_consumer_init(self):
        #successful
        try:
            new = self.success()
        except Exception, e:
            raise AssertionError(
                'Unsuccessful init when successful init expected: {0}{1}'.format(e.__class__.__name__, str(e))
            )

        #missing topic
        self.assertRaises(
            AttributeError,
            self.failure_one
        )

        #missing type
        self.assertRaises(
            AttributeError,
            self.failure_two
        )

    @mock.patch('devour.consumers.pykafka.KafkaClient')
    def test_consumer_configure_simple_consumer_success(self, mocked_client):
        mocked_client.reset_mock()

        mocked_topic = mock.MagicMock()
        mocked_client.return_value.topics.__getitem__.return_value = mocked_topic

        config = {
            "client_config":{
                "hosts":"fakehost:fakeport",
                "ssl_config": None
            }
        }

        self.assertTrue(self.cls._configure(**config))
        mocked_client.assert_called_once_with(hosts='fakehost:fakeport', ssl_config=None)
        mocked_client.return_value.topics.__getitem__.assert_called_once_with('topic')
        mocked_topic.get_simple_consumer.assert_called_once()

    @mock.patch('devour.consumers.pykafka.KafkaClient')
    def test_basic_consumption(self, mocked_client):
        mocked_client.reset_mock()

        messages = [
            'Hi there!',
            "Wahoo!"
        ]
        mocked_topic = mock.MagicMock()
        mocked_topic.get_simple_consumer.return_value = self.generate_mocked_consumer(messages)
        mocked_client.return_value.topics.__getitem__.return_value = mocked_topic

        config = {
            "client_config":{
                "hosts":"fakehost:fakeport",
                "ssl_config": None
            }
        }

        self.assertTrue(self.cls._configure(**config))
        ret = self.cls._consume()
        self.assertFalse(ret)

        self.digest.assert_has_calls(
            [
                mock.call(messages[0]),
                mock.call(messages[1])
            ]
        )

    def test_digest_not_implemented_default(self):
        cls = self.generate_subclass(
            {
                'consumer_topic':'topic',
                'consumer_type':'simple_consumer'
            }
        )

        self.assertRaises(
            NotImplementedError,
            cls
        )

    def test_digest_not_implemented_custom(self):
        cls = self.generate_subclass(
            {
                'consumer_topic':'topic',
                'consumer_type':'simple_consumer'
            }
        )

        self.assertRaises(
            NotImplementedError,
            cls
        )

    def test_config_fails_before_config(self):
        cls = self.generate_subclass(
            {
                'consumer_topic':'topic',
                'consumer_type':'simple_consumer'
            },
            {
                'digest':mock.MagicMock()
            }
        )()

        self.assertRaises(
            exceptions.DevourConfigException,
            cls._consume
        )
