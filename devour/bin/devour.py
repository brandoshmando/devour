import os, sys, argparse

def get_config():
    pass

def parse_args(args):
    p = argparse.ArgumentParser()
    p.add_argument('consumer_name')

    return p.parse_args(args)

def main():
    parsed = parse_args(sys.argv[1:])
    config_dict = get_config()
    # get routes from settings module
    # validate route/object exists
    # get config dict from settings module
    # replace any passed in args in config dict
    # validate config dict
    # instantiate object
    # call ._configure
    pass

if __name__ == '__main__':
    main()
