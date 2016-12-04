try:
    import pykafka
except ImportError:
    raise ImportError('devour requires pykafka and its dependencies')
