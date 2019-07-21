import sys
from contextlib import contextmanager


def get_required_params(params, required_params):
    return {param: params[param] for param in required_params}


def get_posiable_params(params, posiable_params):
    return {param: params[param] for param in posiable_params if param in params.keys()}


@contextmanager
def redirect_stdout(out):
    stdout = sys.stdout
    try:
        yield out
    finally:
        sys.stdout = stdout


class FileStr(str):
    def write(self, in_str):
        self += in_str
