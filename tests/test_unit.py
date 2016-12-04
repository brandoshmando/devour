import mock
from unittest import TestCase
from devour.consumers import DevourConsumer


class BaseTest(TestCase):
    def generate_subclass(self, attrs, funcs={}, base=DevourConsumer):
        """
        :attrs: dictionary of attrs to be set on consumer. must be one of 'argnames'.
            :key: str attr name
            :val: str value
        :funcs: dictionary of functions

        """

        name = "TestDevourConsumer"
        argnames = [
            'consumer_topic',
            'consumer_type',
            'consumer_digest',
            'consumer'
        ]

        for key,val in attrs.items():
            if key not in argnames:
                raise TypeError(' {0} is not a valid argname for generating test consumer'.format(key))
            elif not isinstance(val, str):
                raise TypeError('value for attr {0} must be string'.format(key))

        for key,val in funcs.items():
            if not callable(val):
                raise TypeError('value for func {0} must be function'.format(key))

        attrs.update(funcs)
        subclass = type(name, (DevourConsumer,), attrs)
        return subclass

    def generate_mocked_consumer(self, messages):
        """
        :messages: list of messages to iterate through in test
        """

        consumer = mock.MagicMock()
        formatted_messages = []
        for m in messages:
            mocked_message = mock.Mock()
            mocked_property = mock.PropertyMock(return_value=m)
            type(mocked_message).value = mocked_property
            formatted_messages.append(mocked_message)

        consumer.__iter__.return_value = formatted_messages

        return consumer

class TestConsumer(BaseTest):
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
