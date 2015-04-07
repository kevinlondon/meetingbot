import functools


def memoize(obj):
    # from https://wiki.python.org/moin/PythonDecoratorLibrary
    cache = obj.cache = {}

    @functools.wraps(obj)
    def memoizer(*args, **kwargs):
        if args not in cache:
            cache[args] = obj(*args, **kwargs)
        return cache[args]
    return memoizer
