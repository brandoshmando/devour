CONFIG_SCHEMA = {
    'hosts':                             {'type': str, 'required': True},
    'zookeeper_hosts':                   {'type': str, 'required': False},
    'socket_timeout_ms':                 {'type': int, 'required': False},
    'offsets_channel_socket_timeout_ms': {'type': int, 'required': False},
    'use_greenlets':                     {'type': bool, 'required': False},
    'exclude_internal_topics':           {'type': bool, 'required': False},
    'source_address':                    {'type': str, 'required': False},
    'broker_version':                    {'type': str, 'required': False}
}
