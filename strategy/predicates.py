
def opponentReachesGoal():
    "The ball is directly between our goal and the opponent"
    return False

def existsGoalKick():
    "There is an opportunity to score"
    return False

def collision():
    "We are colliding with the opponent"
    return False

def headonCollision():
    "We are moving against each other"
    return False

def opponentIsFar():
    "The opponent can hardly affect what we are doing"
    return False

def opponentReachesUs():
    "The opponent could reach us if we do an action"
    return False

def opponentReachesBall():
    "The opponent could reach the ball if we do an action"
    return False

def existsDirectionalKick():
    "There is an opportunity to kick the ball away from our goal"
    return False

def opponentIsClose():
    "The opponent is very close to us, but not necessarily blocking"
    return False

def opponentBlocksBall():
    "We can't get to the ball because the opponent is on the way"
    return False

def ballIsStuck():
    "The ball is stuck in some inaccessible spot"
    return False

def canDefend():
    "We can block the way to the ball"
    return False

def ballIsMoving():
    "The ball is moving"
    return False

def ballIsStationary():
    "The ball is not moving"
    return False

def canIntercept():
    "We can move to intercept the ball"
    return False

def opponentIsMoving():
    "The opponent is moving"
    return False

def opponentIsStationary():
    "The opponent is not moving"
    return False

def holdingBall():
    "We are holding the ball--it is in front of us and moves with us"
    return False

def facingTargetGoal():
    "We are facing the opponent's goal area"
    return False
