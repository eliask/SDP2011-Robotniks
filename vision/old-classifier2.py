import math
from utils import *

class Entity:
    dist = 10000
    A = None
    B = None

    def __init__(self, A, B, dist):
        self.dist = dist
        self.A = A
        self.B = B

class Robot(cv.CvBox2D):
     dirmarker = None
     dDist = -1
     T = None
     Tdist = -1


#     def __init__(self, box):
#         self.box = box


# The possible range of width/height for each object;
# in format: ( min_w, max_w, min_h, max_h )
# where width is defined as the larger dimension
Sizes = { 'ball'      : (5,  15,  5, 15),
          'T'         : (35, 45, 25, 35),
          'robot'     : (50, 70, 35, 50),
          'dirmarker' : (3,  12, 3,  12),
        }

RobotPartMaxDist = 30

class Classifier:

    def classify(self, pos):
        """
        :: dict( label -> [ (CvBox2D, CvRect) ] )
           -> dict( label -> (CvBox2D, CvBox2D) )

        Takes as input the positions of the detected features.

        Outputs the positions of the ball and the robots, coupled with
        their features, such as the bounding box of the direction marker
        and the coloured T. Either of the markers could potentially be
        missing from the output, but we do as much as we can here to infer
        some of the missing features.

        Below is a description of the position entities gives as input:

        objects - any foreground objects that remain after background
                  subtraction -- extremely reliable at detecting the
                  objects, but contains some noisy bits too at random
                  places.

        yellow - the yellow T and the ball. The yellow T should be first
                 in the list and should only be missing if it is missing
                 from the picture. The ball is slightly larger in this
                 than with the 'proper' mask/

        blue   - The blue T and little else. Should be very reliable. In all
                 normal circumstances, the blue T will be first in the list,
                 as it should be the largest feature.

        ball   - The ball and probably nothing else. Very reliable at
                 detecting the ball. Again, in normal circumstances the
                 actual ball should be first on the list.
        """
        self.detectBall(pos['ball'])
        self.detectRobots(pos)

        if len(self.balls) > 1:
            print "Warning: multiple balls detected"
        if len(self.robots) > 2:
            print "Warning: more than two robots detected"

        print self.balls[0]
        return (self.robots, self.balls)

    def detectBall(self, ballPos):
        self.balls = []
        for oBox in self.getBoxes(ballPos):
            if not self.sizeMatch(oBox, 'ball'):
                continue
            self.balls.append(oBox)

    def detectRobots(self, pos):
        self.robots = []
        for oBox in self.getBoxes(pos['objects']):
            if not self.sizeMatch(oBox, 'robot'):
                continue
            self.robots.append(oBox) #Robot(oBox) )

        self.detectRobotDirmarkers(pos)
        self.detectYellowT(pos)
        self.detectBlueT(pos)
        self.detectRobotSides()

    def detectRobotSides(self):
        for robot in self.robots:
            yellow, yDist = self.getClosest(robot, self.yellowT)
            blue,   bDist = self.getClosest(robot, self.blueT)
            if yDist == -1 and bDist == -1:
                del robot
                continue
            elif bDist == -1 or yDist < bDist:
                robot.side = 'yellow'
                robot.Tdist = yDist
            else:
                robot.side = 'blue'
                robot.Tdist = bDist

            if robot.Tdist > RobotPartMaxDist:
                del robot

        print "Self.Robots:", len(self.robots)
        print "Robot/T distances:", [r.Tdist for r in self.robots]

    def detectRobotDirmarkers(self, pos):
        self.dirmarkers = []
        for robot in self.robots:
            # TODO: test whether the center of the dirmarker is inside
            # the robot body
            dirmarker, dist = self.getClosest(robot, self.dirmarkers)
            if dist == -1 or dist > RobotPartMaxDist:
                continue
            else:
                robot.dirmarker = dirmarker
                robot.dDist = dist

    def detectYellowT(self, pos):
        self.yellowT = []
        for oBox in self.getBoxes(pos['yellow']):
            if not self.sizeMatch(oBox, 'T'):
                continue
            self.yellowT.append(oBox)

    def detectBlueT(self, pos):
        self.blueT = []
        for oBox in self.getBoxes(pos['blue']):
            if not self.sizeMatch(oBox, 'T'):
                continue
            self.blueT.append(oBox)

    # Maybe refactor these functions into a Box class or something
    def getClosest(self, theBox, boxes):
        if len(boxes) == 0:
            return None, -1
        s = sorted(boxes, key=lambda x: self.boxDist(theBox, x))
        return s[0], self.boxDist(theBox, s[0])

    def boxDist(self, A, B):
        x1, y1 =  BoxCenterPos(A)
        x2, y2 =  BoxCenterPos(B)
        return math.sqrt( (x2 - x1)**2 + (y2 - y1)**2 )

    def getBoxes(self, struct):
        return [ x[0] for x in struct ]

    def getSize(self, box):
        width = max(box.size.width, box.size.height)
        height = min(box.size.width, box.size.height)
        return width, height

    def sizeMatch(self, obj, name):
        width, height = self.getSize(obj)
        print  Sizes[name][0], width, Sizes[name][1], \
            Sizes[name][2], height, Sizes[name][3]

        if  Sizes[name][0] < width  < Sizes[name][1] \
        and Sizes[name][2] < height < Sizes[name][3]:
            return True
        else:
            return False

