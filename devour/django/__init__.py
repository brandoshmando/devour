try:
    import django
except ImportError:
    raise ImportError('devour requires django to be installed when using ProducerModel')
import os

os.environ.setdefault('KAFKA_SETTINGS_PATH', os.environ.get('DJANGO_SETTINGS_MODULE'))
