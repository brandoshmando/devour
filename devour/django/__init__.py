try:
    import django
except ImportError:
    raise ImportError('devour requires django to be installed when using ProducerModel')

import os
from devour.handlers import ClientHandler

os.environ.setdefault('KAFKA_SETTINGS_PATH', os.environ.get('DJANGO_SETTINGS_MODULE'))

default_app_config = 'spout.apps.SpoutConfig'

kafka = ClientHandler()
