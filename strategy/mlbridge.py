from common.utils import *
from common.world import *
from communication.interface import *
from math import *
from strategy import Strategy
from subprocess import Popen, PIPE
import ML.ML_pb2
import logging, cPickle, random

class MLBridge(Strategy):

    def __init__(self, *args):
        Strategy.__init__(self, *args)
        self.log = logging.getLogger("strategy.mlbridge")
        self.log.setLevel(logging.DEBUG)
        self.p = Popen('ML/ml', stdin=PIPE, stdout=PIPE)
        self.chooseTarget()
        self.log.debug("Reading the list of actions")
        self.get_actions_list()
        self.iter = 0
        self.log.debug("Reading trial max_time")
        self.max_time = int( self.p.stdout.readline().strip() )

    def read_message(self):
        msg = ""
        while True:
            line = self.p.stdout.readline()
            if line.strip() != "END":
                msg += line
            else:
                break
        return msg

    def get_actions_list(self):
        msg = self.read_message()
        self.actions = cPickle.loads(msg)

    def peek_future(self):
        "Give the ML component the effects of all actions"
        self.sim.save_state()
        for a in self.actions:
            # self.eval_action(*a)
            # self.sim.update_objects()
            self.passState()
            #self.sim.load_state()

    def get_state(self):
        WS = ML_pb2.WorldState()
        msg = self.read_message()
        WS.ParseFromString( msg[:-1] )
        return WS

    def run_simulator(self):
        "The mode for "
        while True:
            if self.p.stdout.readline().strip() == "END":
                self.iter = 0
                self.log.info("Exiting simulator mode")
                return

            state = self.get_state()
            self.sim.set_state(state)
            self.peek_future()


    def run(self):
        "Run strategy off of the current state of the World."

        if self.iter > self.max_time:
            self.log.info("Going to simulator mode")
            return self.run_simulator()

        self.log.debug("Passing state to subprocess")
        self.passState()
        #self.giveReward()
        self.log.debug("Getting chosen action back from subprocess")
        self.peek_future()
        self.get_action()
        self.log.debug("done")

    def chooseTarget(self):
        "Choose a new target for moving"
        self.goal_x = random.randint(60,560)
        self.goal_y = random.randint(80,360)
        self.goal_orient = 2*pi*random.random() - pi

    def giveReward(self):
        if dist(state_pos(state), goal.pos) < 10:
            # Spend at most about 0.5 extra seconds correcting our orientation
            state_orient = state[4]
            reward = -0,5 * abs(goal.orientation - state_orient)/pi
            self.state.reward = reward
        else:
            self.state.reward = -1.0/dt

    def passState(self):
        "Tell the agent the current state of the world"

        self.state = ML.ML_pb2.WorldState()
        me = self.world.getSelf()
        self.state.robot.pos_x = int(me.pos[0])
        self.state.robot.pos_y = int(me.pos[1])
        self.state.robot.vel_x = me.velocity[0]
        self.state.robot.vel_y = me.velocity[1]
        self.state.robot.angle = me.orientation
        self.state.robot.ang_v = me.ang_v
        self.state.robot.left_angle = me.wheel_left.body.angle
        self.state.robot.right_angle = me.wheel_right.body.angle

        ball = self.world.getBall()
        self.state.ball.pos_x = int(ball.pos[0])
        self.state.ball.pos_y = int(ball.pos[1])
        self.state.ball.vel_x = ball.velocity[0]
        self.state.ball.vel_y = ball.velocity[1]

        print >>self.p.stdin, self.state.SerializeToString()
        print >>self.p.stdin, "END"

        # print >>self.p.stdin, "%d" % self.world.me.pos[0]
        # print >>self.p.stdin, "%d" % self.world.me.pos[1]
        # print >>self.p.stdin, "%.3f" % self.world.me.velocity[0]
        # print >>self.p.stdin, "%.3f" % self.world.me.velocity[1]
        # print >>self.p.stdin, "%.3f" % self.world.me.orientation
        # print >>self.p.stdin, "%.3f" % self.world.me.ang_v

    def get_action(self):
        line = self.p.stdout.readline().strip()
        #print "STUFF:", line
        if line == 'RESET':
            return self.chooseTarget()

        params = line.split('|')
        #print "PARAMS:", params
        self.eval_action(*map(int, params))

    def eval_action(self, driveL, driveR, steerL, steerR):
        self.drive_left(driveL)
        self.drive_right(driveR)
        self.steer_left(steerL)
        self.steer_right(steerR)
        #self.sendMessage()
