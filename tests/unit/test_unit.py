import mock
from unittest import TestCase
from devour.consumers import DevourConsumer
from test_utils import DevourTestMixin

class TestConsumer(TestCase, DevourTestMixin):
    def test_consumer__init__(self):
        #successful
        try:
            new = self.generate_subclass(
                {
                    'consumer_topic':'topic',
                    'consumer_type':'simple_consumer'
                }
            )
        except Exception, e:
            raise AssertionError(
                'Unsuccessful init when successful init expected: {0}{1}'.format(e.__class__.__name__, str(e))
            )

        #missing topic
        self.assertRaises(
            AttributeError,
            self.generate_subclass(
                {'consumer_type': 'simple_consumer'}
            )
        )

        #missing type
        self.assertRaises(
            AttributeError,
            self.generate_subclass(
                {'consumer_topic': 'topic'}
            )
        )

    @mock.patch('devour.consumers.pykafka.KafkaClient')
    def test_consumer_configure_simple_consumer_success(self, mocked_client):
        mocked_client.reset_mock()

        mocked_topic = mock.MagicMock()
        mocked_client.return_value.topics.__getitem__.return_value = mocked_topic

        def digest(self):
            pass

        cls = self.generate_subclass(
            {
                'consumer_topic':'topic',
                'consumer_type':'simple_consumer'
            },
            {
                'digest': digest
            }
        )()

        config = {
            "client_config":{
                "hosts":"fakehost:fakeport",
                "ssl_config": None
            }
        }

        ret = cls._configure(**config)

        self.assertIsNotNone(cls.consumer)
        self.assertTrue(ret)
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

        digest = mock.MagicMock()

        cls = self.generate_subclass(
            {
                'consumer_topic':'topic',
                'consumer_type':'simple_consumer'
            },
            {
                'digest': digest
            }
        )()

        config = {
            "client_config":{
                "hosts":"fakehost:fakeport",
                "ssl_config": None
            }
        }

        self.assertTrue(cls._configure(**config))

        ret = cls._consume()
        self.assertFalse(ret)

        digest.assert_has_calls(
            [
                mock.call(messages[0]),
                mock.call(messages[1])
            ]
        )
