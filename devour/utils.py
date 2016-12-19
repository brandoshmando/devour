import sys, os
from contextlib import contextmanager

from devour import exceptions

@contextmanager
def cwd():
    # get og state on enter
    in_path = os.getcwd() in sys.path
    if not in_path:
        sys.path.insert(0, os.getcwd())
    yield
    # if og state not in path, remove
    if not in_path:
        try:
            sys.path.remove(os.getcwd())
        except ValueError:
            pass

def load_module(path):
    with cwd():
        try:
            __import__(path)
            mod = sys.modules[path]
        except KeyError, ImportError:
            raise exceptions.DevourConfigException('module does not exist at path %s' % path)

        return mod

def load_consumer_class(path):
    with cwd():
        split_path = path.split('.')
        cls_name = split_path.pop(-1)
        joined_path = '.'.join(split_path)

        mod = load_module(joined_path)

        try:
            cls = getattr(mod, cls_name)
        except AttributeError:
            pass

        return cls
