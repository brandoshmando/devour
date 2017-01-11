import os, sys, argparse
from .. import exceptions
from ..utils.loaders import load_module, load_consumer_class
from .schemas import CONFIG_SCHEMA

def validate_config(config):
    for attr,req in CONFIG_SCHEMA.items():
        value = config.get(attr)
        if value:
            if not isinstance(value, req['type']):
                raise exceptions.DevourConfigException('%s is not of type %s' % (attr, req['type']))
        else:
            if req['required']:
                raise exceptions.DevourConfigException('value for %s is required in DEVOUR_CONFIG' % attr)
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
            'missing setting %s in %s file.' % (desc, os.basename(settings.__file__)))

    try:
        # get consumer class and instantiate
        cls = load_consumer_class(routes[parsed.consumer_name])()
    except KeyError:
        raise exceptions.DevourConfigException("consumer class with name '%s' not found in DEVOUR_ROUTES" % parsed.consumer_name)

    cls.configure(config)
    cls.consume()

    #TODO:
    # replace any command line args in config dict

if __name__ == '__main__':
    main()
