from pygame.locals import *
import common.world

class World(common.world.World):

    Friction = 0.03

    def __init__(self, ourColour):
        common.world.World.__init__(self, ourColour)
        self.name = "Simulated World"
        self.ents = {}

    def updatePredictions(self):
        pass

    def updateAttributes():
        self.convertMeasurements()

    def updateWorld():
        pass
    def getSelf(self):
        # TODO: resolve the actual self from user input somehow
        return self.ents['blue']

    def getOpponent(self):
        return self.ents['yellow']

    def openLog(self):
        pass # No anomalies to record

    # def getSelf(self):
    #     return self.us
    # def getOpponent(self):
    #     return self.them
    def getBall(self):
        return self.ents['ball']
    def myPos(self):
        return self.getSelf().pos
    def opponentPos(self):
        return self.getOpponent().pos
