import random


def random_seed(seed):
    def wrap(f):
        def wrapped(*args, **kwargs):
            state = random.getstate()
            random.seed(seed)
            f(*args, **kwargs)
            random.setstate(state)

        return wrapped

    return wrap
