import sys
from contextlib import contextmanager


def get_required_params(params, required_params):
    return {param: params[param] for param in required_params}


def get_possible_params(params, possible_params):
    return {param: params[param] for param in possible_params if param in params.keys()}


def get_required_fields(obj, fields):
    return {field: getattr(obj, field) for field in fields}


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
