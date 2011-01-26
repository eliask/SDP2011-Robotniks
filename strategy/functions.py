from math import *
from .common.utils import *

def getKickingPosition():
    """Get kicking position and orientation.

    Get the position and orientation for us to kick the ball "nicely".
    """
    pass

def move(dest, destAngle):
    "Move directly(?) to destination"
    pass

def constainedMove(dest, destAngle, avoid):
    "Move while avoiding specified object(s)"
    pass

def computeGoalKicks():
    ball = self.ents['ball']
    targetGoal = Magic

    # TODO: also add ball.left/right/etc. rays
    pos = entCenter(ball)
    successes = [ createRay(targetGoal, pos, radians(angle))
                  for angle in range(360) ]

    # TODO: do further processing to determine the best,
    # "non-accidental" clusters
    return successes

def createRay(targetGoal, pos, angle):
    """Simulate the trajectory of an idealised ball.

    targetGoal['score'](x0, x1) is a scoring function that returns a
    utility value between -1 and 1. If we hit the right goal, we get
    maximum utility, and minimum for the wrong one. The two arguments
    x0 and x1 are the starting position and the tested position,
    respectively. If we get a bit further towards the goals
    """
    scorefn = targetGoal['score']
    createRay(scorefn, pos, pos, angle, 3)

def createRay(scorefn, pos0, pos, angle, maxBounces):
    # TODO: handle collisions with robots
    if maxBounces == 0:
        return scorefn(pos0, pos)

    X,Y = pos
    if -pi/2 <= angle <= pi/2:
        dx = Pitch.right - X
    else:
        pitchX = X - Pitch.left

    if 0 <= angle <= pi:
        dy = Pitch.top - Y
    else:
        dy = Y - Pitch.bottom

    hitX = X + dy * tan(angle)
    if hitX < 0:
        imagX = hitX - dx
        if angle == 0:
            # this should only happen inside the goal area
            return scorefn(pos0, (hitX, pos[1]))
        else:
            hitY = Pitch.top + imagX / tan(angle)

    pos = hitX, hitY
    score = scorefn(pos0, pos)
    if abs(score) == 1:
        return score
    else:
        angle = reflectRay(hitX, hitY, angle)
        createRay(targetGoal, pos0, pos, angle, maxBounces-1)


def reflectRay(angle, hitX, hitY):
    # Deal with small numerical inaccuracies
    epsilon = 1e-6
    hitX += epsilon*cos(angle)
    hitY += epsilon*sin(angle)
    if hitY <= Pitch.top or hitY >= Pitch.bottom:
        return angle - pi
    if hitX <= Pitch.left or hitX >= Pitch.right:
        return pi - angle

def computeIntercepts():
    """Compute the possible ways to intercept a moving ball.

    The idea behind our interception approach is to first move to the
    part of the projected trajectory that's closest to us and then
    adjusting our orientation accordingly. If we have time, approach
    the ball by going "backwards" its trajectory.
    """
    pass
