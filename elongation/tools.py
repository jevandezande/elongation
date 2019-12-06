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


def smooth_curve(ys, box_pts=True):
    """
    Smooth a curve.

    Assumes that the ys are uniformly distributed. Returns output of length
    `max(ys, box_pts)`, boundary effects are visible.

    :param ys: points to smooth
    :param box_pts: number of data points to convolve, if True, use 3
    :return: smoothed points
    """
    if box_pts is True:
        box_pts = 3

    box = np.ones(box_pts) / box_pts
    return np.convolve(ys, box, mode='same')
