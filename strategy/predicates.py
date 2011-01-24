class PredicateStore:

    def opponentReachesGoal(self):
        "The ball is directly between our goal and the opponent"
        return False

    def existsGoalKick(self):
        "There is an opportunity to score"
        return False

    def collision(self):
        "We are colliding with the opponent"
        return False

    def headonCollision(self):
        "We are moving against each other"
        return False

    def opponentIsFar(self):
        "The opponent can hardly affect what we are doing"
        return False

    def opponentReachesUs(self):
        "The opponent could reach us if we do an action"
        return False

    def opponentReachesBall(self):
        "The opponent could reach the ball if we do an action"
        return False

    def existsDirectionalKick(self):
        "There is an opportunity to kick the ball away from our goal"
        return False

    def opponentIsClose(self):
        "The opponent is very close to us, but not necessarily blocking"
        return False

    def opponentBlocksBall(self):
        "We can't get to the ball because the opponent is on the way"
        return False

    def ballIsStuck(self):
        "The ball is stuck in some inaccessible spot"
        return False

    def canDefend(self):
        "We can block the way to the ball"
        return False

    def ballIsMoving(self):
        "The ball is moving"
        return False

    def ballIsStationary(self):
        "The ball is not moving"
        return False

    def canIntercept(self):
        "We can move to intercept the ball"
        return False

    def opponentIsMoving(self):
        "The opponent is moving"
        return False

    def opponentIsStationary(self):
        "The opponent is not moving"
        return False

    def holdingBall(self):
        "We are holding the ball--it is in front of us and moves with us"
        return False

    def facingTargetGoal(self):
        "We are facing the opponent's goal area"
        return False

    def canKick(self):
        "We are able to hit the ball with the kicker"
        return False
