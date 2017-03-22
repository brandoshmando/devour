SIMPLE_CONSUMER_CONFIG = {
    'reset_offset_on_start': True,
    'auto_offset_reset': 0
}

BALANCED_CONSUMER_CONFIG = {
    'consumer_group': 'math_consumers',
    'reset_offset_on_start': False,
    'auto_commit_enable': True
}
