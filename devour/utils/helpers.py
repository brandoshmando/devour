import sys, os
from contextlib import contextmanager
from devour import exceptions, validators

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


def validate_config(validator, config):
    for attr,req in validator['data'].items():
        value = config.get(attr)
        if value:
            if req.get('type') == 'nested':
                validator = getattr(validators, req['nested_validator'])
                validate_config(validator, value)
            else:
                if not isinstance(value, req['type']):
                    raise exceptions.DevourConfigException('{0} is not of type {1}'.format(attr, req['type'].__name__))

                if req.get('dependents'):
                    for dep in req['dependents']:
                        if not config.get(dep):
                            raise exceptions.DevourConfigException('{0} requires {1} atrribute to be set'.format(attr, dep))
        else:
            if req['required']:
                raise exceptions.DevourConfigException('value for {0} is required in Devour {1} configuration'.format(attr, validator['type']))

    return True
