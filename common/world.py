from utils import *
import time
from math import *

from entities import Robot

class World(object):

    # Lengths are in millimetres
    PitchWidth   = 1215
    PitchLength  = 2240
    ballDiameter = 45
    goalLength   = 585

    max_states   = 5000
    states = []

    vHorizon = 6   # How many past states to use when calculating
                   # velocity
    vWeight  = 0.5 # How much weight to give to the latest 'raw'
                   # velocity vs. the recent past average

    # The entities we are interested in
    entityNames = ('ball', 'blue', 'yellow')

    def __init__(self, ourColour = None):
        self.time = time.time()
        self.openLog()

        self.ourColour = ourColour
        assert ourColour in ('blue', 'yellow'), \
            "Legal robot colour is required"

        self.ents = {}

    def openLog(self):
        self.log = open('anomalities.txt', 'a')

    def update(self, time, ents):
        self.time = time
        self.ents = ents
        self.updatePredictions()
        self.updateAttributes()
        self.updateStates()
        self.updateWorld()

    def __getPos(self, ent):
        x,y = centerPos(ent)
        return (x,y)

    def __getRobot(self, ent):
        robot = Robot()
        robot.pos = self.__getPos(ent)
        robot.velocity = ent['velocity']
        robot.orientation = ent['orient']
        #robot.direction = ent['direction']

    def getSelf(self):
        return self.__getRobot( self.us )
    def getOpponent(self):
        return self.__getRobot( self.them )

    def getBall(self):
        ball = Ball()
        ball.pos = self.__getPos( self.ents['ball'] )
        ball.velocity = self.ents['ball']['velocity']

    def updateStates(self):
        self.ents['time'] = self.time
        self.states.append(self.ents)
        if len(self.states) > self.max_states:
            del self.states[0]

    def updatePredictions(self):
        """Construct a predicted world state

        The predictions made here are later used to reconcile new
        percepts with our knowledge of the way the world works.
        """
        self.predictBall()
        self.predictRobots()

    def updateAttributes(self):
        self.assignSides()
        self.convertMeasurements()
        self.updateBall()
        self.updateRobots()
        self.updateVelocities()

    def assignSides(self):
        self.us = self.ents[self.ourColour]
        if self.ourColour == 'blue':
            self.them = self.ents['yellow']
        else:
            self.them = self.ents['blue']

    def updateWorld(self):
        """Add missing entities or delete contradictory ones

        In case some essential entities are missing, do our best to
        compensate for that, i.e., reconstruct them based on our
        knowledge about them from the past states.

        If, on the other hand, we see things suddenly teleporting
        somewhere else, we probably
        """
        try:
            for name in ('blue', 'yellow'):
                e1 = self.states[-1][name]
                e2 = self.states[-2][name]

                print e2['orient'] - e1['orient']
                if abs(e2['orient'] - e1['orient']) > pi/5:
                    print >>self.log, e1, e2

        except (IndexError, TypeError): pass

    def predictBall(self):
        pass

    def predictRobots(self):
        pass

    def convertMeasurements(self):
        "Convert image measures to real-world measures"
        pass

    def updateBall(self):
        """Decide where the ball is.

        self.ents contains a list of potential balls. To decide which
        one is the actual ball, we pick the one that is closest to the
        predicted ball position.

        Initially we look for the ball near the center, or as close to
        the center as possible.
        """
        # TODO: implement as per description
        self.ents['ball'] = None
        if self.ents['balls']:
            self.ents['ball'] = self.ents['balls'][0]

    def updateRobots(self):
        pass

    def updateVelocities(self):
        for name in self.entityNames:
            if not self.ents[name]:
                continue

            # We assume we haven't got the start signal in the first
            # couple of frames
            if len(self.states) < self.vHorizon:
                self.ents[name]['velocity'] = np.array([0, 0])
                continue

            # TODO: fix the hack
            self.ents[name]['velocity'] = np.array([0, 0])

            # Do this until we have object interpolation working
            # Or maybe check self.states[*][name] != None after all...
            try:
                avgV = self.averageVelocities(name, self.states[self.vHorizon:-2])
                v0 = centerPos(self.states[-3][name])
                v1 = centerPos(self.states[-1][name])
                newV = (v1-v0)*self.vWeight + avgV*(1-self.vWeight)
                self.ents[name]['velocity'] = newV
            except TypeError:
                pass


    def averageVelocities(self, name, states):
        if len(states) == 0:
            return np.array([0, 0])

        V0 = []; V1 = []
        for state in states:
            v0, v1 = state[name]['velocity']
            V0.append(v0)
            V1.append(v1)
        return np.array( sum(V0)/len(V0), sum(V1)/len(V1) )

class ReversedWorld(World):
    "See us as the other robot - useful if we have two AIs"
    def getSelf(self):
        return super(ReversedWorld, self).getOpponent()
    def getOpponent(self):
        return super(ReversedWorld, self).getSelf()
