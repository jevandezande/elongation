import numpy as np

import more_itertools as mit


class MyIter(mit.peekable):
    """
    Simple class for making it easier to debug reading of files.
    """
    def __init__(self, iterable):
        self._index = 0
        self._line = None
        super().__init__(iterable)

    def __next__(self):
        self._index += 1
        self._line = super().__next__()
        return self._line


def read_key_value(line, separator='='):
    key, *value = line.split(separator)
    return key.strip(), separator.join(value).strip()


def try_to_num(in_str):
    for f in (int, float):
        try:
            return f(in_str)
        except Exception as e:
            pass
    return in_str


def compare_dictionaries(dict1, dict2):
    """
    Compare two dictionaries

    :return: True if the same, False if not
    """
    if len(dict1) != len(dict2):
        return False

    for key in dict1:
        try:
            val1, val2 = dict1[key], dict2[key]
            if val1 != val2:  # different values
                return False
        except KeyError:  # different keys
            return False
        except ValueError:  # non-comparable types
            if isinstance(val1, dict):
                if not compare_dictionaries(val1, val2):
                    return False
            elif any(val1 != val2):  # Compare all values
                return False
    return True
