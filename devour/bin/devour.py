import os, sys, argparse
from .. import exceptions
from ..utils.loaders import load_module, load_consumer_class
from ..utils.helpers import validate_config
from .schemas import CONFIG_SCHEMA

def validate_config(config):
    for attr,req in CONFIG_SCHEMA.items():
        value = config.get(attr)
        if value:
            if not isinstance(value, req['type']):
                raise exceptions.DevourConfigException('{0} is not of type {1}'.format(attr, req['type']))
        else:
            if req['required']:
                raise exceptions.DevourConfigException('value for {0} is required in DEVOUR_CONFIG'.format(attr))
    return True

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
        config = getattr(settings, 'DEVOUR_CONFIG')
    except AttributeError:
        if routes:
            desc = 'DEVOUR_CONFIG'
        else:
            desc = 'DEVOUR_ROUTES'
        raise exceptions.DevourConfigException(
            'missing setting {0} in {1} file.'.format(desc, os.basename(settings.__file__)))

    #validate client config
    validate_config(CONFIG_SCHEMA, config)

    try:
        # get consumer class and instantiate
        cls = load_consumer_class(routes[parsed.consumer_name])()
    except KeyError:
        raise exceptions.DevourConfigException("consumer class with name '{0}' not found in DEVOUR_ROUTES".format(parsed.consumer_name))

    cls.configure(config)
    cls.consume()

    #TODO:
    # replace any command line args in config dict

if __name__ == '__main__':
    main()
