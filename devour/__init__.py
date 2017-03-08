try:
    import pykafka
except ImportError:
    raise ImportError('devour requires pykafka and its dependencies')
from devour.handlers import ClientHandler

# persists connection per thread
kafka = ClientHandler()
