import sys


def load_module(path):
    __import__(path)
    try:
        mod = sys.modules[path]
    except KeyError:
        pass

    return mod

def load_consumer_class(path):
    split_path = path.split('.')
    cls_name = split_path.pop(-1)
    joined_path = '.'.join(split_path)

    mod = load_module(joined_path)

    try:
        cls = getattr(mod, cls_name)
    except AttributeError:
        pass

    return cls
