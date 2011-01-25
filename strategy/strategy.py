from .communication.interface import *

class Strategy(RobotInterface):
    """The base strategy class.

    This class exists to allow the easy implementation of different
    strategies. Not to be used directly.
    """

    def __init__(self, world, interface):
        self.world = world

        # Make our commands point to the interface
        commands = [ method for method in RobotInterface.__dict__.keys()
                     if method[:2] != '__' ]
        for attr in commands:
            self.__setattr__(attr, interface.__getattribute__(attr))

    def run(self):
        return NotImplemented
