try:
    import pykafka
except ImportError:
    raise ImportError('devour requires pykafka and its dependencies')
from devour.handlers import ClientHandler

try:
    import django
    default_app_config = 'devour.django.apps.DevourConfig'
except ImportError:
    pass


# persists connection per thread
kafka = ClientHandler()
