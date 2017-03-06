from pykafka.common import OffsetType
from kazoo.client import KazooClient

CONFIG_VALIDATOR = {
    'type': 'client',
    'data': {
        'hosts':                             {'type': str, 'required': True},
        'zookeeper_hosts':                   {'type': str, 'required': False},
        'ssl_config':                        {'type': 'nested', 'required': False, 'nested_validator':'SSL_VALIDATOR'},
        'socket_timeout_ms':                 {'type': int, 'required': False},
        'offsets_channel_socket_timeout_ms': {'type': int, 'required': False},
        'use_greenlets':                     {'type': bool, 'required': False},
        'exclude_internal_topics':           {'type': bool, 'required': False},
        'source_address':                    {'type': str, 'required': False},
        'broker_version':                    {'type': str, 'required': False}
    }
}

SSL_VALIDATOR = {
    'type': 'ssl',
    'data': {
        'cafile': {'type': str, 'required': True},
        'certfile': {'type': str, 'required': False},
        'keyfile': {'type': str, 'required': False},
        'password': {'type': str, 'required': False},
    }
}

SIMPLE_CONSUMER_VALIDATOR = {
    'type': 'consumer',
    'data': {
        'consumer_group':            {'type': bytes, 'required': False},
        'fetch_message_max_bytes':   {'type': int, 'required': False},
        'num_consumer_fetchers':     {'type': int, 'required': False},
        'auto_commit_enable':        {'type': bool, 'required': False, 'dependents':['consumer_group']},
        'auto_commit_interval_ms':   {'type': int, 'required': False},
        'queued_max_messages':       {'type': int, 'required': False},
        'fetch_min_bytes':           {'type': int, 'required': False},
        'fetch_wait_max_ms':         {'type': int, 'required': False},
        'offsets_channel_backoff_ms':{'type': int, 'required': False},
        'offsets_commit_max_retries':{'type': int, 'required': False},
        'auto_offset_reset':         {'type': OffsetType, 'required': False},
        'consumer_timeout_ms':       {'type': int, 'required': False},
        'auto_start':                {'type': bool, 'required': False},
        'reset_offset_on_start':     {'type': bool, 'required': False},
        'compacted_topic':           {'type': bool, 'required': False},
        'generation_id':             {'type': int, 'required': False},
        'consumer_id':               {'type': bytes, 'required': False},
        'log_name':                  {'type': str, 'required': False}
    }
}

BALANCED_CONSUMER_VALIDATOR  = {
    'type': 'consumer',
    'data': {
        'consumer_group':                 {'type': bytes, 'required': True},
        'managed':                        {'type': bool, 'required': False},
        'fetch_message_max_bytes':        {'type': int, 'required': False},
        'num_consumer_fetchers':          {'type': int, 'required': False},
        'auto_commit_enable':             {'type': bool, 'required': False, 'dependents':['consumer_group']},
        'auto_commit_interval_ms':        {'type': int, 'required': False},
        'queued_max_messages':            {'type': int, 'required': False},
        'fetch_min_bytes':                {'type': int, 'required': False},
        'fetch_wait_max_ms':              {'type': int, 'required': False},
        'offsets_channel_backoff_ms':     {'type': int, 'required': False},
        'offsets_commit_max_retries':     {'type': int, 'required': False},
        'auto_offset_reset':              {'type': OffsetType, 'required': False},
        'consumer_timeout_ms':            {'type': int, 'required': False},
        'auto_start':                     {'type': bool, 'required': False},
        'reset_offset_on_start':          {'type': bool, 'required': False},
        'compacted_topic':                {'type': bool, 'required': False},
        'zookeeper_connection_timeout_ms':{'type': int, 'required': False},
        'zookeeper_connect':              {'type': str, 'required': False},
        'zookeeper':                      {'type': KazooClient, 'required': False},
        'use_rdkafka':                    {'type': bool, 'required': False},
        'rebalance_backoff_ms':           {'type': int, 'required': False},
        'rebalance_max_retries':          {'type': int, 'required': False},
        'log_name':                       {'type': str, 'required': False}
    }
}
