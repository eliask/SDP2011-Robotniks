from math import *
from common.utils import *

def getKickingPosition():
    """Get kicking position and orientation.

    Get the position and orientation for us to kick the ball "nicely".
    """
    pass

def computeGoalKicks(my_goal, opponent_goal, ball, opponent, resolution):
    """Return the best directions to kick the ball towards

    Currently this is incomplete. Some thought is required as to what
    constitutes a good position. If there are multiple possible kicks
    side by side, the "maximum margin" kick should usually be chosen.
    """
    def avg(x):
        if len(x) == 0: return 0
        return sum(x)/len(x)

    def goal_score(goal, ball):
        goal_len = dist(*goal)
        D = dist(ball, goal[0]), dist(ball, goal[1])
        if min(D) > 200:
            return 0
        if D[0] <= goal_len and D[1] <= goal_len:
            return 1

        return 0
        if D[0] < D[1]:
            return D[0] / sum(D)
        else:
            return D[1] / sum(D)

    def scorefn(ball):
        my = goal_score(my_goal, ball)
        op = goal_score(opponent_goal, ball)
        print ball, my_goal, opponent_goal, my, op
        #assert my <= 0 or op <= 0
        return my + op

    successes = [ createRay(scorefn, resolution,
                            opponent, ball, radians(angle), 1)
                  for angle in range(360) ]

    w=0.5; n=9
    gauss1d = np.exp( -0.5 * w/n * np.array(range(-(n-1), n, 2))**2 )
    gauss1d /= sum(gauss1d)

    wraparound = int(np.ceil(n/2.0))
    wrapped = successes[-wraparound:] + successes + successes[:wraparound]
    convolved = np.convolve(gauss1d, successes, 'same')
    unwrapped = convolved[wraparound : len(successes)]

    return successes #unwrapped

def createRay(scorefn, resolution, opponent, ball, angle, maxBounces):
    """Simulate the trajectory of an idealised ball.

    scorefn(x0, x1) is a scoring function that returns a
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
        return scorefn(ball)

    X,Y = ball
    if -pi/2 <= angle <= pi/2:
        dx = resolution[0] - X
    else:
        dx = 0 - X

    if 0 <= angle <= pi:
        dy = 0 - Y
    else:
        dy = resolution[1] - Y

    #print "STUFF:",X,Y,angle,dy,dx
    hitX = X + dy * tan(angle)
    if hitX < 0:
        imagX = hitX - dx
        if angle == 0:
            # this should only happen inside the goal area
            return scorefn((hitX, ball[1]))

    imagX = hitX - dx
    hitY = Y + dx * cos(angle)
    if hitX < 0 or hitX > resolution[0]:
        hitY = 0 + imagX / tan(angle)

    ball = hitX, hitY
    score = scorefn(ball)
    if abs(score) == 1:
        return score
    else:
        angle = reflectRay(resolution, hitX, hitY, angle)
        return createRay(scorefn, resolution, opponent, ball, angle, maxBounces-1)

def reflectRay(resolution, angle, hitX, hitY):
    # Deal with small numerical inaccuracies
    epsilon = 1e-6
    hitX += epsilon*cos(angle)
    hitY += epsilon*sin(angle)
    if hitY <= 0 or hitY >= resolution[1]:
        return angle - pi
    if hitX <= 0 or hitX >= resolution[0]:
        return pi - angle

def computeIntercepts():
    """Compute the possible ways to intercept a moving ball.

    The idea behind our interception approach is to first move to the
    part of the projected trajectory that's closest to us and then
    adjusting our orientation accordingly. If we have time, approach
    the ball by going "backwards" its trajectory.
    """
    pass
