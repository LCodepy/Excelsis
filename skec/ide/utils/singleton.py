class Singleton(type):

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls.__name__ in cls._instances:
            return cls._instances[cls.__name__]

        cls._instances[cls.__name__] = super().__call__(*args, **kwargs)
        return cls._instances[cls.__name__]


def singleton(cls):
    def wrapper():
        class A(metaclass=Singleton):
            pass
        a = A()
        a.__name__ = cls.__name__
        a.__dict__ = dict(cls.__dict__)
        return a
    return wrapper


