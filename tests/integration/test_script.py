import mock
import argparse
from unittest import TestCase
from devour import exceptions
from devour.bin.devour import parse_args

class TestScript(TestCase):
    def test_parse_args_success(self):
        arg_map = {
            'consumer_name': 'test'
        }

        ret = parse_args(arg_map.values())
        self.assertEqual(ret.consumer_name, arg_map['consumer_name'])

    def test_parse_args_failure(self):
        arg_map = {}

        self.assertRaises(
            SystemExit,
            parse_args,
            arg_map.values()
        )
