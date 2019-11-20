import random
import re


def random_seed(seed):
    def wrap(f):
        def wrapped(*args, **kwargs):
            state = random.getstate()
            random.seed(seed)
            f(*args, **kwargs)
            random.setstate(state)

        return wrapped

    return wrap


class regex_matcher:
    """Assert that a given string meets some expectations."""

    def __init__(self, pattern, flags=0):
        self._regex = re.compile(pattern, flags)

    def __eq__(self, actual):
        return bool(self._regex.match(actual))

    def __repr__(self):
        return self._regex.pattern
