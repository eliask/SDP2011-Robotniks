from utils import *
import time
from math import *

class World:

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

    def __init__(self):
        self.time = time.time()
        self.log = open('anomalities.txt', 'a')

    def update(self, time, ents):
        self.time = time
        self.ents = ents
        self.updatePredictions()
        self.updateAttributes()
        self.updateStates()
        self.updateWorld()

    def convertEnt

    def getSelf(self):
        # TODO: resolve the actual self from user input somehow
        return self.ents['blue']

    def getOpponent(self):
        return self.ents['yellow']

    def ballPos(self):
        return self.ents['ball'].pos
        return ball.pos

    def myPos(self):
        return self.getSelf().pos

    def opponentPos(self):
        return self.getOpponent().pos

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
        self.convertMeasurements()
        self.updateBall()
        self.updateRobots()
        self.updateVelocities()

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
                self.ents[name]['velocity'] = (0, 0)
                continue

            # TODO: fix the hack
            self.ents[name]['velocity'] = (0, 0)

            # Do this until we have object interpolation working
            # Or maybe check self.states[*][name] != None after all...
            try:
                avgV = self.averageVelocities(name, self.states[self.vHorizon:-2])
                x0, y0 = centerPos(self.states[-3][name])
                x1, y1 = centerPos(self.states[-1][name])
                newV = ( (x1-x0)*self.vWeight + avgV[0]*(1-self.vWeight),
                         (y1-y0)*self.vWeight + avgV[1]*(1-self.vWeight) )
                self.ents[name]['velocity'] = newV
            except TypeError:
                pass


    def averageVelocities(self, name, states):
        if len(states) == 0:
            return (0, 0)

        V0 = []; V1 = []
        for state in states:
            v0, v1 = state[name]['velocity']
            V0.append(v0)
            V1.append(v1)
        return ( sum(V0)/len(V0), sum(V1)/len(V1) )

