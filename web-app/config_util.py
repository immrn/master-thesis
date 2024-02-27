import os
from typing import List

def getenv_bool(var: str, default: bool) -> bool:
    """!
    Parses var to bool. Raises a TypeError if the value of the env var couldn't be parsed.
    :param var: name of the environment variable
    :param default: default value
    :return: var parsed to bool; default if var doesn't exist
    """
    val = os.getenv(var)
    if val in ['True', 'true', 1]:
        return True
    elif val in ['False', 'false', 0]:
        return False
    elif val is None:
        return default
    else:
        raise TypeError(f'The environment variable "{var}" must be of type bool (valid values: "True" and "False")!')

def getenv_int(var: str, default: int) -> int:
    """!
    Parses var to int. Raises a TypeError if the value of the env var couldn't be parsed.
    :param var: name of the environment variable
    :param default: default value
    :return: var parsed to int; default if var doesn't exist
    """
    val = os.getenv(var)
    if val is None:
        return default
    else:
        try:
            val = int(val)
        except TypeError:
            raise TypeError(f'The environment variable "{var}" must be an int!')
        return val


def getenv_switch_str(var: str, options: List[str], default: str) -> str:
    """!
    Checks if the env var equals one of the options. If not, raises a ValueError.
    :param var: name of the environment variable
    :param options: list of accepted strings
    :param default: default str to return when env var isn't defined
    :return: the str value of the env var
    """
    val = os.getenv(var)
    if val is None:
        return default
    elif val in options:
        return val
    else:
        raise ValueError(f'The environment variable "{var}" has to be on of the following options: {options}')
