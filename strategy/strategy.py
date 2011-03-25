from communication.interface import *
from common.utils import other_colour
import logging

class Strategy(object):
    """The base strategy class.

    This class exists to allow the easy implementation of different
    strategies. Not to be used directly.
    """

    def __init__(self, world, interface, arg=None, sim=None, **kwargs):
        self.arg = arg
        self.sim = sim
        self.world = world
        self.interface = interface

        self.log = logging.getLogger('strategy.%s' % kwargs['name'])

        logging.getLogger("strategy") \
            .info( "Strategy %s started in the %s"
                   % (self.__class__.__name__, world.name) )

    def __getattr__(self, name):
        if hasattr(self.interface, name):
            func = getattr(self.interface, name)
            return lambda *args, **kwargs: \
                func(*args, **kwargs)
        raise AttributeError(name)

    def setColour(self, colour):
        print colour
        self.colour = colour

    def draw(self):
        pass

    def setTarget(self, target):
        self.world.setTarget(self.colour, target)
    def addText(self, text):
        print self.colour, text
        self.world.addText(self.colour, text)

    def getSelf(self):
        return self.world.getRobot(self.colour)

    def getOpponent(self):
        return self.world.getRobot( other_colour(self.colour) )

    def getBall(self):
        return self.world.getBall()

    def getMyGoalPos(self):
        return self.world.getGoalPos(self.colour)

    def getOpponentGoalPos(self):
        return self.world.getGoalPos( other_colour(self.colour) )

    def getMyGoalPoints(self):
        return self.world.getGoalPoints( self.colour )

    def getOpponentGoalPoints(self):
        return self.world.getGoalPoints( other_colour(self.colour) )

    def getBallDecisionPoints(self):
        return self.world.getBallDecisionPoints( self.colour )
    def getBallGoalPoint(self):
        return self.world.getBallGoalPoint( self.colour )

    def run(self):
        raise NotImplemented, "Base AI class - DO NOT USE"

    def getTimeUntil(self, delta):
        if self.sim:
            return time.time() + delta / self.sim.speed
        else:
            return time.time() + delta
