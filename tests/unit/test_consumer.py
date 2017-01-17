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

        self.assertTrue(self.cls.configure(**config))
        mocked_client.assert_called_once_with(hosts='fakehost:fakeport', ssl_config=None, zookeeper_hosts=None)
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

        self.assertTrue(self.cls.configure(**config))
        ret = self.cls.consume()
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
            cls.consume
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

    #test arg validations
    def test_consumer_group_simple_consumer(self):
        arg_dict = {
            'consumer_group': bytes('fakename')
        }

        # valid
        ret = self.cls._validate_config(arg_dict, 'simple_consumer')
        self.assertTrue(ret)
        # invalid
        arg_dict['consumer_group'] = 1
        self.assertRaises(
            exceptions.DevourConfigException,
            self.cls._validate_config,
            config=arg_dict,
            consumer_type='simple_consumer'
        )

    def test_fetch_message_max_bytes_simple_consumer(self):
        arg_dict = {
            'fetch_message_max_bytes': 1
        }

        # valid
        ret = self.cls._validate_config(arg_dict, 'simple_consumer')
        self.assertTrue(ret)
        # invalid
        arg_dict['fetch_message_max_bytes'] = 'invalid'
        self.assertRaises(
            exceptions.DevourConfigException,
            self.cls._validate_config,
            config=arg_dict,
            consumer_type='simple_consumer'
        )

    def test_num_consumer_fetchers_simple_consumer(self):
        arg_dict = {
            'num_consumer_fetchers': 1
        }

        # valid
        ret = self.cls._validate_config(arg_dict, 'simple_consumer')
        self.assertTrue(ret)
        # invalid
        arg_dict['num_consumer_fetchers'] = 'invalid'
        self.assertRaises(
            exceptions.DevourConfigException,
            self.cls._validate_config,
            config=arg_dict,
            consumer_type='simple_consumer'
        )

    def test_auto_commit_enable_simple_consumer(self):
        arg_dict = {
            'consumer_group': 'fakegroup',
            'auto_commit_enable': True
        }

        # valid
        ret = self.cls._validate_config(arg_dict, 'simple_consumer')
        self.assertTrue(ret)
        # invalid
        arg_dict['auto_commit_enable'] = 'invalid'
        self.assertRaises(
            exceptions.DevourConfigException,
            self.cls._validate_config,
            config=arg_dict,
            consumer_type='simple_consumer'
        )
        # missing dependent
        del arg_dict['consumer_group']
        self.assertRaises(
            exceptions.DevourConfigException,
            self.cls._validate_config,
            config=arg_dict,
            consumer_type='simple_consumer'
        )

    def test_auto_commit_interval_ms_simple_consumer(self):
        arg_dict = {
            'auto_commit_interval_ms': 1
        }

        # valid
        ret = self.cls._validate_config(arg_dict, 'simple_consumer')
        self.assertTrue(ret)
        # invalid
        arg_dict['auto_commit_interval_ms'] = 'invalid'
        self.assertRaises(
            exceptions.DevourConfigException,
            self.cls._validate_config,
            config=arg_dict,
            consumer_type='simple_consumer'
        )

    def test_queued_max_messages_simple_consumer(self):
        arg_dict = {
            'queued_max_messages': 1
        }

        # valid
        ret = self.cls._validate_config(arg_dict, 'simple_consumer')
        self.assertTrue(ret)
        # invalid
        arg_dict['queued_max_messages'] = 'invalid'
        self.assertRaises(
            exceptions.DevourConfigException,
            self.cls._validate_config,
            config=arg_dict,
            consumer_type='simple_consumer'
        )

    def test_fetch_min_bytes_simple_consumer(self):
        arg_dict = {
            'fetch_min_bytes': 1
        }

        # valid
        ret = self.cls._validate_config(arg_dict, 'simple_consumer')
        self.assertTrue(ret)
        # invalid
        arg_dict['fetch_min_bytes'] = 'invalid'
        self.assertRaises(
            exceptions.DevourConfigException,
            self.cls._validate_config,
            config=arg_dict,
            consumer_type='simple_consumer'
        )

    def test_fetch_wait_max_ms_simple_consumer(self):
        arg_dict = {
            'fetch_wait_max_ms': 1
        }

        # valid
        ret = self.cls._validate_config(arg_dict, 'simple_consumer')
        self.assertTrue(ret)
        # invalid
        arg_dict['fetch_wait_max_ms'] = 'invalid'
        self.assertRaises(
            exceptions.DevourConfigException,
            self.cls._validate_config,
            config=arg_dict,
            consumer_type='simple_consumer'
        )

    def test_offsets_channel_backoff_ms_simple_consumer(self):
        arg_dict = {
            'offsets_channel_backoff_ms': 1
        }

        # valid
        ret = self.cls._validate_config(arg_dict, 'simple_consumer')
        self.assertTrue(ret)
        # invalid
        arg_dict['offsets_channel_backoff_ms'] = 'invalid'
        self.assertRaises(
            exceptions.DevourConfigException,
            self.cls._validate_config,
            config=arg_dict,
            consumer_type='simple_consumer'
        )

    def test_offsets_commit_max_retries_simple_consumer(self):
        arg_dict = {
            'offsets_commit_max_retries': 1
        }

        # valid
        ret = self.cls._validate_config(arg_dict, 'simple_consumer')
        self.assertTrue(ret)
        # invalid
        arg_dict['offsets_commit_max_retries'] = 'invalid'
        self.assertRaises(
            exceptions.DevourConfigException,
            self.cls._validate_config,
            config=arg_dict,
            consumer_type='simple_consumer'
        )

    def test_auto_offset_reset_simple_consumer(self):
        arg_dict = {
            'auto_offset_reset': OffsetType()
        }

        # valid
        ret = self.cls._validate_config(arg_dict, 'simple_consumer')
        self.assertTrue(ret)
        # invalid
        arg_dict['auto_offset_reset'] = 'invalid'
        self.assertRaises(
            exceptions.DevourConfigException,
            self.cls._validate_config,
            config=arg_dict,
            consumer_type='simple_consumer'
        )

    def test_consumer_timeout_ms_simple_consumer(self):
        arg_dict = {
            'consumer_timeout_ms': 1
        }

        # valid
        ret = self.cls._validate_config(arg_dict, 'simple_consumer')
        self.assertTrue(ret)
        # invalid
        arg_dict['consumer_timeout_ms'] = 'invalid'
        self.assertRaises(
            exceptions.DevourConfigException,
            self.cls._validate_config,
            config=arg_dict,
            consumer_type='simple_consumer'
        )

    def test_auto_start_simple_consumer(self):
        arg_dict = {
            'auto_start': True
        }

        # valid
        ret = self.cls._validate_config(arg_dict, 'simple_consumer')
        self.assertTrue(ret)
        # invalid
        arg_dict['auto_start'] = 'invalid'
        self.assertRaises(
            exceptions.DevourConfigException,
            self.cls._validate_config,
            config=arg_dict,
            consumer_type='simple_consumer'
        )

    def test_reset_offset_on_start_simple_consumer(self):
        arg_dict = {
            'reset_offset_on_start': True
        }

        # valid
        ret = self.cls._validate_config(arg_dict, 'simple_consumer')
        self.assertTrue(ret)
        # invalid
        arg_dict['reset_offset_on_start'] = 'invalid'
        self.assertRaises(
            exceptions.DevourConfigException,
            self.cls._validate_config,
            config=arg_dict,
            consumer_type='simple_consumer'
        )

    def test_compacted_topic_simple_consumer(self):
        arg_dict = {
            'compacted_topic': True
        }

        # valid
        ret = self.cls._validate_config(arg_dict, 'simple_consumer')
        self.assertTrue(ret)
        # invalid
        arg_dict['compacted_topic'] = 'invalid'
        self.assertRaises(
            exceptions.DevourConfigException,
            self.cls._validate_config,
            config=arg_dict,
            consumer_type='simple_consumer'
        )

    def test_generation_id_simple_consumer(self):
        arg_dict = {
            'generation_id': 1
        }

        # valid
        ret = self.cls._validate_config(arg_dict, 'simple_consumer')
        self.assertTrue(ret)
        # invalid
        arg_dict['generation_id'] = 'invalid'
        self.assertRaises(
            exceptions.DevourConfigException,
            self.cls._validate_config,
            config=arg_dict,
            consumer_type='simple_consumer'
        )

    def test_consumer_id_simple_consumer(self):
        arg_dict = {
            'consumer_id': bytes('valid')
        }

        # valid
        ret = self.cls._validate_config(arg_dict, 'simple_consumer')
        self.assertTrue(ret)
        # invalid
        arg_dict['generation_id'] = 'invalid'
        self.assertRaises(
            exceptions.DevourConfigException,
            self.cls._validate_config,
            config=arg_dict,
            consumer_type='simple_consumer'
        )


class TestBalancedConsumerLogic(TestCase, DevourTestMixin):
    def setUp(self):
        self.success = self.generate_subclass(
            {
                'consumer_topic':'topic',
                'consumer_type':'balanced_consumer'
            },
            {
                'digest': mock.MagicMock()
            }
        )

        self.failure_one = self.generate_subclass(
            {'consumer_type': 'balanced_consumer'}
        )

        self.failure_two = self.generate_subclass(
            {'consumer_topic': 'topic'}
        )

        self.digest = mock.MagicMock()

        self.cls = self.generate_subclass(
            {
                'consumer_topic':'topic',
                'consumer_type':'balanced_consumer',
                'dump_raw': True
            },
            {
                'digest': self.digest
            }
        )()


    def test_balanced_consumer_init(self):
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
    def test_configure_balanced_consumer_success(self, mocked_client):
        mocked_client.reset_mock()

        mocked_topic = mock.MagicMock()
        mocked_client.return_value.topics.__getitem__.return_value = mocked_topic

        config = {
            "client_config":{
                "hosts":"fakehost:fakeport",
                "ssl_config": None
            }
        }

        self.assertTrue(self.cls.configure(**config))
        mocked_client.assert_called_once_with(hosts='fakehost:fakeport', ssl_config=None, zookeeper_hosts=None)
        mocked_client.return_value.topics.__getitem__.assert_called_once_with('topic')
        mocked_topic.get_balanced_consumer.assert_called_once()

    @mock.patch('devour.consumers.pykafka.KafkaClient')
    def test_basic_consumption_balanced_consumer(self, mocked_client):
        mocked_client.reset_mock()

        messages = [
            'Hi there!',
            "Wahoo!"
        ]
        mocked_topic = mock.MagicMock()
        mocked_topic.get_balanced_consumer.return_value = self.generate_mocked_consumer(messages)
        mocked_client.return_value.topics.__getitem__.return_value = mocked_topic

        config = {
            "client_config":{
                "hosts":"fakehost:fakeport",
                "ssl_config": None
            }
        }

        self.assertTrue(self.cls.configure(**config))
        ret = self.cls.consume()
        self.assertFalse(ret)

        self.digest.assert_has_calls(
            [
                mock.call(messages[0]),
                mock.call(messages[1])
            ]
        )

    def test_digest_not_implemented_default_balanced_consumer(self):
        cls = self.generate_subclass(
            {
                'consumer_topic':'topic',
                'consumer_type':'balanced_consumer'
            }
        )

        self.assertRaises(
            NotImplementedError,
            cls
        )

    def test_digest_not_implemented_custom_balanced_consumer(self):
        cls = self.generate_subclass(
            {
                'consumer_topic':'topic',
                'consumer_type':'balanced_consumer'
            }
        )

        self.assertRaises(
            NotImplementedError,
            cls
        )

    def test_consume_fails_before_config_balanced_consumer(self):
        cls = self.generate_subclass(
            {
                'consumer_topic':'topic',
                'consumer_type':'balanced_consumer'
            },
            {
                'digest':mock.MagicMock()
            }
        )()

        self.assertRaises(
            exceptions.DevourConfigException,
            cls.consume
        )

class TestBalancedConsumerArgValidation(TestCase, DevourTestMixin):
    def setUp(self):
        self.cls = self.generate_subclass(
            {
                'consumer_topic':'topic',
                'consumer_type':'balanced_consumer'
            },
            {
                'digest': mock.MagicMock()
            }
        )()

    #test arg validations
    def test_consumer_group_balanced_consumer(self):
        arg_dict = {
            'consumer_group': bytes('fakename')
        }

        # valid
        ret = self.cls._validate_config(arg_dict, 'balanced_consumer')
        self.assertTrue(ret)
        # invalid
        arg_dict['consumer_group'] = 1
        self.assertRaises(
            exceptions.DevourConfigException,
            self.cls._validate_config,
            config=arg_dict,
            consumer_type='balanced_consumer'
        )

        # reqiured
        arg_dict['consumer_group'] = None
        self.assertRaises(
            exceptions.DevourConfigException,
            self.cls._validate_config,
            config=arg_dict,
            consumer_type='balanced_consumer'
        )

        del arg_dict['consumer_group']
        self.assertRaises(
            exceptions.DevourConfigException,
            self.cls._validate_config,
            config=arg_dict,
            consumer_type='balanced_consumer'
        )

    def test_fetch_message_max_bytes_balanced_consumer(self):
        arg_dict = {
            'consumer_group': 'fakegroup',
            'fetch_message_max_bytes': 1
        }

        # valid
        ret = self.cls._validate_config(arg_dict, 'balanced_consumer')
        self.assertTrue(ret)
        # invalid
        arg_dict['fetch_message_max_bytes'] = 'invalid'
        self.assertRaises(
            exceptions.DevourConfigException,
            self.cls._validate_config,
            config=arg_dict,
            consumer_type='balanced_consumer'
        )

    def test_num_consumer_fetchers_balanced_consumer(self):
        arg_dict = {
            'consumer_group': 'fakegroup',
            'num_consumer_fetchers': 1
        }

        # valid
        ret = self.cls._validate_config(arg_dict, 'balanced_consumer')
        self.assertTrue(ret)
        # invalid
        arg_dict['num_consumer_fetchers'] = 'invalid'
        self.assertRaises(
            exceptions.DevourConfigException,
            self.cls._validate_config,
            config=arg_dict,
            consumer_type='balanced_consumer'
        )

    def test_auto_commit_enable_balanced_consumer(self):
        arg_dict = {
            'consumer_group': 'fakegroup',
            'auto_commit_enable': True
        }

        # valid
        ret = self.cls._validate_config(arg_dict, 'balanced_consumer')
        self.assertTrue(ret)
        # invalid
        arg_dict['auto_commit_enable'] = 'invalid'
        self.assertRaises(
            exceptions.DevourConfigException,
            self.cls._validate_config,
            config=arg_dict,
            consumer_type='balanced_consumer'
        )
        # missing dependent
        del arg_dict['consumer_group']
        self.assertRaises(
            exceptions.DevourConfigException,
            self.cls._validate_config,
            config=arg_dict,
            consumer_type='balanced_consumer'
        )

    def test_auto_commit_interval_ms_balanced_consumer(self):
        arg_dict = {
            'consumer_group': 'fakegroup',
            'auto_commit_interval_ms': 1
        }

        # valid
        ret = self.cls._validate_config(arg_dict, 'balanced_consumer')
        self.assertTrue(ret)
        # invalid
        arg_dict['auto_commit_interval_ms'] = 'invalid'
        self.assertRaises(
            exceptions.DevourConfigException,
            self.cls._validate_config,
            config=arg_dict,
            consumer_type='balanced_consumer'
        )

    def test_queued_max_messages_balanced_consumer(self):
        arg_dict = {
            'consumer_group': 'fakegroup',
            'queued_max_messages': 1
        }

        # valid
        ret = self.cls._validate_config(arg_dict, 'balanced_consumer')
        self.assertTrue(ret)
        # invalid
        arg_dict['queued_max_messages'] = 'invalid'
        self.assertRaises(
            exceptions.DevourConfigException,
            self.cls._validate_config,
            config=arg_dict,
            consumer_type='balanced_consumer'
        )

    def test_fetch_min_bytes_balanced_consumer(self):
        arg_dict = {
            'consumer_group': 'fakegroup',
            'fetch_min_bytes': 1
        }

        # valid
        ret = self.cls._validate_config(arg_dict, 'balanced_consumer')
        self.assertTrue(ret)
        # invalid
        arg_dict['fetch_min_bytes'] = 'invalid'
        self.assertRaises(
            exceptions.DevourConfigException,
            self.cls._validate_config,
            config=arg_dict,
            consumer_type='balanced_consumer'
        )

    def test_fetch_wait_max_ms_balanced_consumer(self):
        arg_dict = {
            'consumer_group': 'fakegroup',
            'fetch_wait_max_ms': 1
        }

        # valid
        ret = self.cls._validate_config(arg_dict, 'balanced_consumer')
        self.assertTrue(ret)
        # invalid
        arg_dict['fetch_wait_max_ms'] = 'invalid'
        self.assertRaises(
            exceptions.DevourConfigException,
            self.cls._validate_config,
            config=arg_dict,
            consumer_type='balanced_consumer'
        )

    def test_offsets_channel_backoff_ms_balanced_consumer(self):
        arg_dict = {
            'consumer_group': 'fakegroup',
            'offsets_channel_backoff_ms': 1
        }

        # valid
        ret = self.cls._validate_config(arg_dict, 'balanced_consumer')
        self.assertTrue(ret)
        # invalid
        arg_dict['offsets_channel_backoff_ms'] = 'invalid'
        self.assertRaises(
            exceptions.DevourConfigException,
            self.cls._validate_config,
            config=arg_dict,
            consumer_type='balanced_consumer'
        )

    def test_offsets_commit_max_retries_balanced_consumer(self):
        arg_dict = {
            'consumer_group': 'fakegroup',
            'offsets_commit_max_retries': 1
        }

        # valid
        ret = self.cls._validate_config(arg_dict, 'balanced_consumer')
        self.assertTrue(ret)
        # invalid
        arg_dict['offsets_commit_max_retries'] = 'invalid'
        self.assertRaises(
            exceptions.DevourConfigException,
            self.cls._validate_config,
            config=arg_dict,
            consumer_type='balanced_consumer'
        )

    def test_auto_offset_reset_balanced_consumer(self):
        arg_dict = {
            'consumer_group': 'fakegroup',
            'auto_offset_reset': OffsetType()
        }

        # valid
        ret = self.cls._validate_config(arg_dict, 'balanced_consumer')
        self.assertTrue(ret)
        # invalid
        arg_dict['auto_offset_reset'] = 'invalid'
        self.assertRaises(
            exceptions.DevourConfigException,
            self.cls._validate_config,
            config=arg_dict,
            consumer_type='balanced_consumer'
        )

    def test_consumer_timeout_ms_balanced_consumer(self):
        arg_dict = {
            'consumer_group': 'fakegroup',
            'consumer_timeout_ms': 1
        }

        # valid
        ret = self.cls._validate_config(arg_dict, 'balanced_consumer')
        self.assertTrue(ret)
        # invalid
        arg_dict['consumer_timeout_ms'] = 'invalid'
        self.assertRaises(
            exceptions.DevourConfigException,
            self.cls._validate_config,
            config=arg_dict,
            consumer_type='balanced_consumer'
        )

    def test_auto_start_balanced_consumer(self):
        arg_dict = {
            'consumer_group': 'fakegroup',
            'auto_start': True
        }

        # valid
        ret = self.cls._validate_config(arg_dict, 'balanced_consumer')
        self.assertTrue(ret)
        # invalid
        arg_dict['auto_start'] = 'invalid'
        self.assertRaises(
            exceptions.DevourConfigException,
            self.cls._validate_config,
            config=arg_dict,
            consumer_type='balanced_consumer'
        )

    def test_reset_offset_on_start_balanced_consumer(self):
        arg_dict = {
            'consumer_group': 'fakegroup',
            'reset_offset_on_start': True
        }

        # valid
        ret = self.cls._validate_config(arg_dict, 'balanced_consumer')
        self.assertTrue(ret)
        # invalid
        arg_dict['reset_offset_on_start'] = 'invalid'
        self.assertRaises(
            exceptions.DevourConfigException,
            self.cls._validate_config,
            config=arg_dict,
            consumer_type='balanced_consumer'
        )

    def test_compacted_topic_balanced_consumer(self):
        arg_dict = {
            'consumer_group': 'fakegroup',
            'compacted_topic': True
        }

        # valid
        ret = self.cls._validate_config(arg_dict, 'balanced_consumer')
        self.assertTrue(ret)
        # invalid
        arg_dict['compacted_topic'] = 'invalid'
        self.assertRaises(
            exceptions.DevourConfigException,
            self.cls._validate_config,
            config=arg_dict,
            consumer_type='balanced_consumer'
        )
