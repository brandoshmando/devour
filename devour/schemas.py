from pykafka.common import OffsetType

SIMPLE_CONSUMER_SCHEMA = {
    'fetch_message_max_bytes':   {'type': int, 'required': False},
    'num_consumer_fetchers':     {'type': int, 'required': False},
    'auto_commit_enable':        {'type': bool, 'required': False},
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
}
