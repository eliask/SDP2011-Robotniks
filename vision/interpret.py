from utils import *
from math import *

class Interpreter:

    def interpret(self, ents):
        "Currently, add robot orientation for all robots, if possible"
        for robot in ents['robots']:
            self.getOrientation(robot)

    def getOrientation(self, robot):
        self.convertRobotCoordinates(robot)
        angleT   = self.angleT(robot)
        angleDir = self.angleDir(robot)

        # robot['box'].angle only returns an angle between 0 and 90 degrees
        boxAngles = [ degrees(robot['box'].angle) + n*pi/2
                      for n in range(-2, 2+1) ]

        # In case neither the T nor the direction marker is found
        robot['modOrient'] = boxAngles[2]

        angleBox = None
        if angleDir:
            angleBox = sorted( boxAngles, key=lambda x: abs(angleDir - x) )[0]
        elif angleT:
            angleBox = sorted( boxAngles, key=lambda x: abs(angleT - x) )[0]

        robot['orient'] = self.mergeMeasurements(angleBox, angleT, angleDir)

    def mergeMeasurements(self, box, T, dir):
        #print "Angles:", (box, T, dir)
        if dir: return dir
        if T: return T
        if box: return box
        return None

    def angleT(self, robot):
        X, Y = centerPos(robot)
        if robot['T']:
            tX, tY = centerPos(robot['T'])
            dx, dy = tX - X, tY - Y
            return atan2(dy, dx)
        return None

    def angleDir(self, robot):
        X, Y = centerPos(robot)
        if robot['dirmarker']:
            dirX, dirY = centerPos(robot['dirmarker'])
            dx, dy = X - dirX, Y - dirY
            return atan2(dy, dx)
        return None

    def convertRobotCoordinates(self, robot):
        if robot['T']:
            self.convertCoordinates(robot, robot['T'])
        if robot['dirmarker']:
            self.convertCoordinates(robot, robot['dirmarker'])

    def convertCoordinates(self, ent, sub):
        "Convert relative coordinates to absolute"
        R = ent['rect']
        c = sub['box'].center
        r = sub['rect']
        """
        The sub-entity's bounding rectangle's coordinates are
        relative to the parent entity.
        """
        sub['rect'].x = R.x + r.x
        sub['rect'].y = R.y + r.y
        sub['box'].center.x = R.x + c.x
        sub['box'].center.y = R.y + c.y

