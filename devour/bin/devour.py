import os, sys, argparse
from .. import exceptions
from ..utils.loaders import load_module, load_consumer_class
from ..utils.helpers import validate_config
from .schemas import CONFIG_SCHEMA

def parse_args(args):
    p = argparse.ArgumentParser()
    p.add_argument('consumer_name')

    return p.parse_args(args)

def main():
    parsed = parse_args(sys.argv[1:])
    settings_path = os.environ.get('KAFKA_SETTINGS') or 'settings'
    settings = load_module(settings_path)

    try:
        routes = getattr(settings, 'CONSUMER_ROUTES')
    except AttributeError:
        raise exceptions.DevourConfigException(
            'missing setting CONSUMER_ROUTES in {0} file.'.format(os.basename(settings.__file__)))

    try:
        # get consumer class and instantiate
        cls = load_consumer_class(routes[parsed.consumer_name])()
    except KeyError:
        raise exceptions.DevourConfigException("consumer class with name '{0}' not found in CONSUMER_ROUTES".format(parsed.consumer_name))

    # start consuming
    cls.consume()

    #TODO:
    # replace any command line args in config dict

if __name__ == '__main__':
    main()
