from .communication.interface import *
import logging

class Strategy(RobotInterface):
    """The base strategy class.

    This class exists to allow the easy implementation of different
    strategies. Not to be used directly.
    """

    def __init__(self, world, interface):
        self.world = world
        logging.info( "Strategy %s started in the %s"
                      % (self.__class__.__name__, world.name) )

        # Make our commands point to the interface
        commands = [ method for method in RobotInterface.__dict__.keys()
                     if method[:2] != '__' ]
        for attr in commands:
            self.__setattr__(attr, interface.__getattribute__(attr))

    def run(self):
        raise NotImplemented, "Base AI class - DO NOT USE"
