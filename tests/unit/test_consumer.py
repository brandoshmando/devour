import mock
from unittest import TestCase
from pykafka.common import OffsetType

from devour import exceptions
from test_utils import DevourTestMixin

class TestSimpleConsumerLogic(TestCase, DevourTestMixin):
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
                'consumer_type':'simple_consumer',
                'dump_raw': True
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

class TestSimpleConsumerArgValidation(TestCase, DevourTestMixin):
    def setUp(self):
        self.cls = self.generate_subclass(
            {
                'consumer_topic':'topic',
                'consumer_type':'simple_consumer'
            },
            {
                'digest': mock.MagicMock()
            }
        )()

    #test arg validations / setattr
    @mock.patch('devour.consumers.pykafka.KafkaClient')
    def test_fetch_message_max_bytes(self, mocked_client):
        mocked_client.reset_mock()
        mocked_topic = mock.MagicMock()
        mocked_client.return_value.topics.__getitem__.return_value = mocked_topic

        arg_dict = {
            'fetch_message_max_bytes': 1
        }

        # valid
        ret = self.cls._validate_config(arg_dict, 'simple_consumer')
        self.assertTrue(ret)
        # invalid
        arg_dict['fetch_message_max_bytes'] = 'invalid'
        self.assertRaises(
            exceptions.DevourConsumerException,
            self.cls._validate_config,
            config=arg_dict,
            consumer_type='simple_consumer'
        )

    @mock.patch('devour.consumers.pykafka.KafkaClient')
    def test_num_consumer_fetchers(self, mocked_client):
        mocked_client.reset_mock()
        mocked_topic = mock.MagicMock()
        mocked_client.return_value.topics.__getitem__.return_value = mocked_topic

        arg_dict = {
            'num_consumer_fetchers': 1
        }

        # valid
        ret = self.cls._validate_config(arg_dict, 'simple_consumer')
        self.assertTrue(ret)
        # invalid
        arg_dict['num_consumer_fetchers'] = 'invalid'
        self.assertRaises(
            exceptions.DevourConsumerException,
            self.cls._validate_config,
            config=arg_dict,
            consumer_type='simple_consumer'
        )

    @mock.patch('devour.consumers.pykafka.KafkaClient')
    def test_auto_commit_enable(self, mocked_client):
        mocked_client.reset_mock()
        mocked_topic = mock.MagicMock()
        mocked_client.return_value.topics.__getitem__.return_value = mocked_topic

        arg_dict = {
            'auto_commit_enable': True
        }

        # valid
        ret = self.cls._validate_config(arg_dict, 'simple_consumer')
        self.assertTrue(ret)
        # invalid
        arg_dict['auto_commit_enable'] = 'invalid'
        self.assertRaises(
            exceptions.DevourConsumerException,
            self.cls._validate_config,
            config=arg_dict,
            consumer_type='simple_consumer'
        )

    @mock.patch('devour.consumers.pykafka.KafkaClient')
    def test_auto_commit_interval_ms(self, mocked_client):
        mocked_client.reset_mock()
        mocked_topic = mock.MagicMock()
        mocked_client.return_value.topics.__getitem__.return_value = mocked_topic

        arg_dict = {
            'auto_commit_interval_ms': 1
        }

        # valid
        ret = self.cls._validate_config(arg_dict, 'simple_consumer')
        self.assertTrue(ret)
        # invalid
        arg_dict['auto_commit_interval_ms'] = 'invalid'
        self.assertRaises(
            exceptions.DevourConsumerException,
            self.cls._validate_config,
            config=arg_dict,
            consumer_type='simple_consumer'
        )

    @mock.patch('devour.consumers.pykafka.KafkaClient')
    def test_queued_max_messages(self, mocked_client):
        mocked_client.reset_mock()
        mocked_topic = mock.MagicMock()
        mocked_client.return_value.topics.__getitem__.return_value = mocked_topic

        arg_dict = {
            'queued_max_messages': 1
        }

        # valid
        ret = self.cls._validate_config(arg_dict, 'simple_consumer')
        self.assertTrue(ret)
        # invalid
        arg_dict['queued_max_messages'] = 'invalid'
        self.assertRaises(
            exceptions.DevourConsumerException,
            self.cls._validate_config,
            config=arg_dict,
            consumer_type='simple_consumer'
        )

    @mock.patch('devour.consumers.pykafka.KafkaClient')
    def test_fetch_min_bytes(self, mocked_client):
        mocked_client.reset_mock()
        mocked_topic = mock.MagicMock()
        mocked_client.return_value.topics.__getitem__.return_value = mocked_topic

        arg_dict = {
            'fetch_min_bytes': 1
        }

        # valid
        ret = self.cls._validate_config(arg_dict, 'simple_consumer')
        self.assertTrue(ret)
        # invalid
        arg_dict['fetch_min_bytes'] = 'invalid'
        self.assertRaises(
            exceptions.DevourConsumerException,
            self.cls._validate_config,
            config=arg_dict,
            consumer_type='simple_consumer'
        )

    @mock.patch('devour.consumers.pykafka.KafkaClient')
    def test_fetch_wait_max_ms(self, mocked_client):
        mocked_client.reset_mock()
        mocked_topic = mock.MagicMock()
        mocked_client.return_value.topics.__getitem__.return_value = mocked_topic

        arg_dict = {
            'fetch_wait_max_ms': 1
        }

        # valid
        ret = self.cls._validate_config(arg_dict, 'simple_consumer')
        self.assertTrue(ret)
        # invalid
        arg_dict['fetch_wait_max_ms'] = 'invalid'
        self.assertRaises(
            exceptions.DevourConsumerException,
            self.cls._validate_config,
            config=arg_dict,
            consumer_type='simple_consumer'
        )

    @mock.patch('devour.consumers.pykafka.KafkaClient')
    def test_offsets_channel_backoff_ms(self, mocked_client):
        mocked_client.reset_mock()
        mocked_topic = mock.MagicMock()
        mocked_client.return_value.topics.__getitem__.return_value = mocked_topic

        arg_dict = {
            'offsets_channel_backoff_ms': 1
        }

        # valid
        ret = self.cls._validate_config(arg_dict, 'simple_consumer')
        self.assertTrue(ret)
        # invalid
        arg_dict['offsets_channel_backoff_ms'] = 'invalid'
        self.assertRaises(
            exceptions.DevourConsumerException,
            self.cls._validate_config,
            config=arg_dict,
            consumer_type='simple_consumer'
        )

    @mock.patch('devour.consumers.pykafka.KafkaClient')
    def test_offsets_commit_max_retries(self, mocked_client):
        mocked_client.reset_mock()
        mocked_topic = mock.MagicMock()
        mocked_client.return_value.topics.__getitem__.return_value = mocked_topic

        arg_dict = {
            'offsets_commit_max_retries': 1
        }

        # valid
        ret = self.cls._validate_config(arg_dict, 'simple_consumer')
        self.assertTrue(ret)
        # invalid
        arg_dict['offsets_commit_max_retries'] = 'invalid'
        self.assertRaises(
            exceptions.DevourConsumerException,
            self.cls._validate_config,
            config=arg_dict,
            consumer_type='simple_consumer'
        )

    @mock.patch('devour.consumers.pykafka.KafkaClient')
    def test_auto_offset_reset(self, mocked_client):
        mocked_client.reset_mock()
        mocked_topic = mock.MagicMock()
        mocked_client.return_value.topics.__getitem__.return_value = mocked_topic

        arg_dict = {
            'auto_offset_reset': OffsetType()
        }

        # valid
        ret = self.cls._validate_config(arg_dict, 'simple_consumer')
        self.assertTrue(ret)
        # invalid
        arg_dict['auto_offset_reset'] = 'invalid'
        self.assertRaises(
            exceptions.DevourConsumerException,
            self.cls._validate_config,
            config=arg_dict,
            consumer_type='simple_consumer'
        )

    @mock.patch('devour.consumers.pykafka.KafkaClient')
    def test_consumer_timeout_ms(self, mocked_client):
        mocked_client.reset_mock()
        mocked_topic = mock.MagicMock()
        mocked_client.return_value.topics.__getitem__.return_value = mocked_topic

        arg_dict = {
            'consumer_timeout_ms': 1
        }

        # valid
        ret = self.cls._validate_config(arg_dict, 'simple_consumer')
        self.assertTrue(ret)
        # invalid
        arg_dict['consumer_timeout_ms'] = 'invalid'
        self.assertRaises(
            exceptions.DevourConsumerException,
            self.cls._validate_config,
            config=arg_dict,
            consumer_type='simple_consumer'
        )

    @mock.patch('devour.consumers.pykafka.KafkaClient')
    def test_auto_start(self, mocked_client):
        mocked_client.reset_mock()
        mocked_topic = mock.MagicMock()
        mocked_client.return_value.topics.__getitem__.return_value = mocked_topic

        arg_dict = {
            'auto_start': True
        }

        # valid
        ret = self.cls._validate_config(arg_dict, 'simple_consumer')
        self.assertTrue(ret)
        # invalid
        arg_dict['auto_start'] = 'invalid'
        self.assertRaises(
            exceptions.DevourConsumerException,
            self.cls._validate_config,
            config=arg_dict,
            consumer_type='simple_consumer'
        )

    @mock.patch('devour.consumers.pykafka.KafkaClient')
    def test_reset_offset_on_start(self, mocked_client):
        mocked_client.reset_mock()
        mocked_topic = mock.MagicMock()
        mocked_client.return_value.topics.__getitem__.return_value = mocked_topic

        arg_dict = {
            'reset_offset_on_start': True
        }

        # valid
        ret = self.cls._validate_config(arg_dict, 'simple_consumer')
        self.assertTrue(ret)
        # invalid
        arg_dict['reset_offset_on_start'] = 'invalid'
        self.assertRaises(
            exceptions.DevourConsumerException,
            self.cls._validate_config,
            config=arg_dict,
            consumer_type='simple_consumer'
        )

    @mock.patch('devour.consumers.pykafka.KafkaClient')
    def test_compacted_topic(self, mocked_client):
        mocked_client.reset_mock()
        mocked_topic = mock.MagicMock()
        mocked_client.return_value.topics.__getitem__.return_value = mocked_topic

        arg_dict = {
            'compacted_topic': True
        }

        # valid
        ret = self.cls._validate_config(arg_dict, 'simple_consumer')
        self.assertTrue(ret)
        # invalid
        arg_dict['compacted_topic'] = 'invalid'
        self.assertRaises(
            exceptions.DevourConsumerException,
            self.cls._validate_config,
            config=arg_dict,
            consumer_type='simple_consumer'
        )

    @mock.patch('devour.consumers.pykafka.KafkaClient')
    def test_generation_id(self, mocked_client):
        mocked_client.reset_mock()
        mocked_topic = mock.MagicMock()
        mocked_client.return_value.topics.__getitem__.return_value = mocked_topic

        arg_dict = {
            'generation_id': 1
        }

        # valid
        ret = self.cls._validate_config(arg_dict, 'simple_consumer')
        self.assertTrue(ret)
        # invalid
        arg_dict['generation_id'] = 'invalid'
        self.assertRaises(
            exceptions.DevourConsumerException,
            self.cls._validate_config,
            config=arg_dict,
            consumer_type='simple_consumer'
        )

    @mock.patch('devour.consumers.pykafka.KafkaClient')
    def test_consumer_id(self, mocked_client):
        mocked_client.reset_mock()
        mocked_topic = mock.MagicMock()
        mocked_client.return_value.topics.__getitem__.return_value = mocked_topic

        arg_dict = {
            'consumer_id': bytes('valid')
        }

        # valid
        ret = self.cls._validate_config(arg_dict, 'simple_consumer')
        self.assertTrue(ret)
        # invalid
        arg_dict['generation_id'] = 'invalid'
        self.assertRaises(
            exceptions.DevourConsumerException,
            self.cls._validate_config,
            config=arg_dict,
            consumer_type='simple_consumer'
        )
