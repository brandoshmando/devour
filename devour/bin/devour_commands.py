import os, sys, argparse
from devour.exceptions import DevourConfigException
from devour.utils.loaders import load_module, load_consumer_class
from devour.utils.helpers import validate_config

def parse_args(args):
    p = argparse.ArgumentParser()
    p.add_argument('method')
    p.add_argument('consumer_name')

    return p.parse_args(args)

def main():
    parsed = parse_args(sys.argv[1:])
    if parsed.method == 'consume':
        consume(parsed.consumer_name)

def consume(consumer_name):
    settings_path = os.environ.get('KAFKA_SETTINGS_PATH') or 'settings'
    settings = load_module(settings_path)

    try:
        kafka = getattr(settings, 'KAFKA_CONFIG')
        routes = kafka['consumer_routes']
    except AttributeError:
        raise DevourConfigException(
            'missing setting CONSUMER_ROUTES in settings.'
        )
    except KeyError:
        raise DevourConfigException(
            'missing  consumer_routes in KAFKA_CONFIG'
        )

    try:
        # get consumer class and instantiate
        cls = load_consumer_class(routes[consumer_name])()
    except KeyError:
        raise DevourConfigException("consumer class with name '{0}' not found in CONSUMER_ROUTES".format(consumer_name))

    # start consuming
    cls.consume()

    #TODO:
    # replace any command line args in config dict

if __name__ == '__main__':
    main()
