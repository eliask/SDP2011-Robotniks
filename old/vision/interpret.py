from common.utils import *
from math import *

class Interpreter:
    """Get as much out of a a single state as we can.

    The Interpreter acts as a stateless sanity-checker and derived
    feature computer for entities.

    The Interpreter does the following:
    * The orientation of the robots is computed using the coloured Ts
      or the direction markers on top of them.
    * Robot (sub-) feature coordinates are converted from relative to
      absolute coordinates, to make further processing easier.
    * The entities 'yellow' and 'blue' are created from the list of
      robots, corresponding to the apprent robots where that possess
      the coloured Ts
    * If we can deduce but not recognise the side of an apparent
      robot, we do so, and if we can eliminate apparent robots by
      knowing the sides of two, we do so too.
    """

    def interpret(self, ents):
        "Currently, add robot orientation for all robots, if possible"
        for robot in ents['robots']:
            self.getOrientation(robot)

    def getOrientation(self, robot):
        self.convertRobotCoordinates(robot)
        angleT   = self.angleT(robot)
        angleDir = self.angleDir(robot)

        boxAngles = entOrientation(robot)

        # In case neither the T nor the direction marker is found
        robot['modOrient'] = boxAngles # N.B.: could be []

        angleBox = None
        if boxAngles:
            if angleDir:
                angleBox = sorted( boxAngles,
                                   key=lambda x: abs(angleDir - x) )[0]
            elif angleT:
                angleBox = sorted( boxAngles,
                                   key=lambda x: abs(angleT - x) )[0]

        robot['orient'] = self.mergeMeasurements(angleBox, angleT, angleDir)

    def mergeMeasurements(self, box, T, dir):
        #print "Angles:", (box, T, dir)
        if dir: return dir
        if T: return T
        if box: return box
        return None

    def angleT(self, robot):
        X, Y = entCenter(robot)
        if robot['T']:
            tX, tY = entCenter(robot['T'])
            dx, dy = tX - X, tY - Y
            return atan2(dy, dx)
        return None

    def angleDir(self, robot):
        X, Y = entCenter(robot)
        if robot['dirmarker']:
            dirX, dirY = entCenter(robot['dirmarker'])
            dx, dy = X - dirX, Y - dirY
            return atan2(dy, dx)
        return None

    def convertAngle(self, angle):
        "Convert from atan2 output to [0,2pi)"
        if angle >= 0:
            return angle
        else:
            return -pi-angle

    def convertRobotCoordinates(self, robot):
        if robot['T']:
            self.convertCoordinates(robot, robot['T'])
        if robot['dirmarker']:
            self.convertCoordinates(robot, robot['dirmarker'])

    def convertCoordinates(self, ent, sub):
        "Convert relative coordinates to absolute"
        # The sub-entity's bounding rectangle's coordinates are
        # relative to the parent entity.
        w,h = entRect(sub)[2:]
        sub['rect'] = list( entRect(ent)[:2] + entRect(sub)[:2] )

        sub['rect'] += [w,h]
        sub['box'] = ( entCenter(ent) + entCenter(sub),
                       entDim(sub), entAngle(sub) )
