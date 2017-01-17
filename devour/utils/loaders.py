import sys, os
from contextlib import contextmanager

from devour import exceptions
from devour.utils.helpers import cwd

def load_module(path):
    with cwd():
        try:
            __import__(path)
            mod = sys.modules[path]
        except KeyError, ImportError:
            raise exceptions.DevourConfigException('module does not exist at path {0}'.format(path))

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
            raise exceptions.DevourConfigException('consumer class {0} is not defined'.format(cls_name))

        return cls
