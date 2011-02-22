from communication.interface import *
import logging

class Strategy(object):
    """The base strategy class.

    This class exists to allow the easy implementation of different
    strategies. Not to be used directly.
    """

    def __init__(self, world, interface, arg=None, sim=None):
        self.arg = arg
        self.sim = sim
        self.world = world
        self.interface = interface

        logging.getLogger("strategy") \
            .info( "Strategy %s started in the %s"
                   % (self.__class__.__name__, world.name) )

    def __getattr__(self, name):
        if hasattr(self.interface, name):
            func = getattr(self.interface, name)
            return lambda *args, **kwargs: \
                func(*args, **kwargs)
        raise AttributeError(name)

    def run(self):
        raise NotImplemented, "Base AI class - DO NOT USE"
