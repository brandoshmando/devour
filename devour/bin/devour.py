import os, sys, argparse, atexit
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
    settings_path = os.environ.get('DEVOUR_SETTINGS') or 'settings'
    settings = load_module(settings_path)

    try:
        routes = getattr(settings, 'DEVOUR_ROUTES')
    except AttributeError:
        raise exceptions.DevourConfigException(
            'missing setting DEVOUR_ROUTES in {0} file.'.format(os.basename(settings.__file__)))

    #validate client config
    validate_config(CONFIG_SCHEMA, config)

    try:
        # get consumer class and instantiate
        cls = load_consumer_class(routes[parsed.consumer_name])()
    except KeyError:
        raise exceptions.DevourConfigException("consumer class with name '{0}' not found in DEVOUR_ROUTES".format(parsed.consumer_name))

    atexit.register(cls.client.stop_all_producers)
    cls.consume()

    #TODO:
    # replace any command line args in config dict

if __name__ == '__main__':
    main()
