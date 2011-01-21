from math import *
from utils import *

def computeGoalKicks():
    bX, bY = centerPos(self.ents['ball'])

    targetGoal = Magic
    assert targetGoal['right'] or targetGoal['left']

    if targetGoal['right']:
        angles = range(90) + range(270, 360)
    else:
        angles = range(90,270)

    for angle in angles:
        angle = radians(angle)


