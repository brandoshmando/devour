import sys, os
from contextlib import contextmanager

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
