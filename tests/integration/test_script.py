import mock
import argparse
from unittest import TestCase
from devour import exceptions
from devour.bin.devour_commands import parse_args
from devour.validators import CONFIG_VALIDATOR
from devour.utils.helpers import validate_config

class TestScript(TestCase):
    def test_parse_args_success(self):
        args = ['consume', 'test']
        ret = parse_args(args)
        self.assertEqual(ret.method, args[0])
        self.assertEqual(ret.consumer_name, args[1])

    def test_parse_args_failure(self):
        arg_map = {}

        self.assertRaises(
            SystemExit,
            parse_args,
            arg_map.values()
        )

class TestConfigValidation(TestCase):
    def test_hosts(self):
        # valid
        args_dict = {
            'hosts':'fakehost:fakeport'
        }

        ret = validate_config(CONFIG_VALIDATOR, args_dict)
        self.assertTrue(ret)

        # invalid
        args_dict['hosts'] = 1
        self.assertRaises(
            exceptions.DevourConfigException,
            validate_config,
            CONFIG_VALIDATOR,
            args_dict
        )

        # missing / empty
        self.assertRaises(
            exceptions.DevourConfigException,
            validate_config,
            CONFIG_VALIDATOR,
            args_dict
        )

        args_dict['hosts'] = None
        self.assertRaises(
            exceptions.DevourConfigException,
            validate_config,
            CONFIG_VALIDATOR,
            args_dict
        )

    def test_zookeeper_hosts(self):
        # valid
        args_dict = {
            'hosts':'fakehost:fakeport',
            'zookeeper_hosts':'fakehost:fakeport'
        }

        ret = validate_config(CONFIG_VALIDATOR, args_dict)
        self.assertTrue(ret)

        # invalid
        args_dict['zookeeper_hosts'] = 1
        self.assertRaises(
            exceptions.DevourConfigException,
            validate_config,
            CONFIG_VALIDATOR,
            args_dict
        )

    def test_socket_timeout_ms(self):
        # valid
        args_dict = {
            'hosts':'fakehost:fakeport',
            'socket_timeout_ms': 1
        }

        ret = validate_config(CONFIG_VALIDATOR, args_dict)
        self.assertTrue(ret)

        # invalid
        args_dict['socket_timeout_ms'] = 'invalid'
        self.assertRaises(
            exceptions.DevourConfigException,
            validate_config,
            CONFIG_VALIDATOR,
            args_dict
        )

    def test_offsets_channel_socket_timeout_ms(self):
        # valid
        args_dict = {
            'hosts':'fakehost:fakeport',
            'offsets_channel_socket_timeout_ms': 1
        }

        ret = validate_config(CONFIG_VALIDATOR, args_dict)
        self.assertTrue(ret)

        # invalid
        args_dict['offsets_channel_socket_timeout_ms'] = 'invalid'
        self.assertRaises(
            exceptions.DevourConfigException,
            validate_config,
            CONFIG_VALIDATOR,
            args_dict
        )

    def test_use_greenlets(self):
        # valid
        args_dict = {
            'hosts':'fakehost:fakeport',
            'use_greenlets': True
        }

        ret = validate_config(CONFIG_VALIDATOR, args_dict)
        self.assertTrue(ret)

        # invalid
        args_dict['use_greenlets'] = 'invalid'
        self.assertRaises(
            exceptions.DevourConfigException,
            validate_config,
            CONFIG_VALIDATOR,
            args_dict
        )

    def test_exclude_internal_topics(self):
        # valid
        args_dict = {
            'hosts':'fakehost:fakeport',
            'exclude_internal_topics': True
        }

        ret = validate_config(CONFIG_VALIDATOR, args_dict)
        self.assertTrue(ret)

        # invalid
        args_dict['exclude_internal_topics'] = 'invalid'
        self.assertRaises(
            exceptions.DevourConfigException,
            validate_config,
            CONFIG_VALIDATOR,
            args_dict
        )

    def test_source_address(self):
        # valid
        args_dict = {
            'hosts':'fakehost:fakeport',
            'source_address': 'fakehost:fakeport'
        }

        ret = validate_config(CONFIG_VALIDATOR, args_dict)
        self.assertTrue(ret)

        # invalid
        args_dict['source_address'] = 1
        self.assertRaises(
            exceptions.DevourConfigException,
            validate_config,
            CONFIG_VALIDATOR,
            args_dict
        )

    def test_broker_version(self):
        # valid
        args_dict = {
            'hosts':'fakehost:fakeport',
            'broker_version': '0.8'
        }

        ret = validate_config(CONFIG_VALIDATOR, args_dict)
        self.assertTrue(ret)

        # invalid
        args_dict['broker_version'] = 1
        self.assertRaises(
            exceptions.DevourConfigException,
            validate_config,
            CONFIG_VALIDATOR,
            args_dict
        )

    def test_ssl_config(self):
        #valid
        args_dict = {
            'hosts':'fakehost:fakeport',
            'ssl_config': {
                'cafile': './fake/path/',
                'certfile': './fake/path/',
                'keyfile': './fake/path/',
                'password': './fake/path/'
            }
        }

        ret = validate_config(CONFIG_VALIDATOR, args_dict)
        self.assertTrue(ret)

        args_dict['ssl_config']['certfile'] = 1
        self.assertRaises(
            exceptions.DevourConfigException,
            validate_config,
            CONFIG_VALIDATOR,
            args_dict
        )

        del args_dict['ssl_config']['cafile']
        self.assertRaises(
            exceptions.DevourConfigException,
            validate_config,
            CONFIG_VALIDATOR,
            args_dict
        )
