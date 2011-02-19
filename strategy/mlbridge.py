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
        self.log.setLevel(logging.INFO)

        cmd = ['ML/ml']
        if self.arg:
            cmd.append( self.arg )
        self.p = Popen(cmd, stdin=PIPE, stdout=PIPE)

        self.chooseTarget()
        self.log.debug("Reading the list of actions")
        self.get_actions_list()
        self.iter = 0
        self.log.debug("Reading trial max_time")
        self.max_time = int( self.getline() )

    def getline_raw(self):
        return self.p.stdout.readline()
    def getline(self):
        return self.p.stdout.readline().strip()

    def read_message(self):
        msg = ""
        while True:
            line = self.getline_raw()
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
        self.log.debug("evaluating actions applied to the current state")
        self.sim.save_state()
        for a in self.actions:
            self.eval_action(*a)
            self.sim.update_objects()
            self.passState()
            self.sim.load_state()

    def get_state(self):
        msg = self.read_message()
        #print msg
        WS = ML.ML_pb2.WorldState()
        WS.ParseFromString( msg[:-1] )
        return WS

    def run_simulator(self):
        "The mode for "
        N = 0
        while True:
            line = self.getline()
            if line == "END":
                self.iter = 0
                self.log.info("Exiting simulator mode")
                return

            #self.log.debug("iteration: %d", N); N += 1
            self.log.debug("Getting world state")
            state = self.get_state()
            self.log.debug("Setting a new simulator state")
            self.sim.set_state(state)
            self.peek_future()

    def maybe_reset_world(self):
        "Reset the simulator world if the robot is stuck somewhere"
        state = self.construct_state()
        state.robot.pos_x = random.randint(120,560)
        state.robot.pos_y = random.randint(100,300)
        state.robot.vel_x = random.randint(0,30)
        state.robot.vel_y = random.randint(0,30)
        state.robot.angle = radians(random.randint(0,359))
        #state.robot.ang_v = random.random()
        state.robot.left_angle = radians(random.randint(0,359))
        state.robot.right_angle = radians(random.randint(0,359))
        self.sim.set_state(state)

    def run(self):
        "Run strategy off of the current state of the World."

        self.iter += 1
        if self.iter > self.max_time:
            self.log.info("Entering simulator mode")
            self.run_simulator()
            self.maybe_reset_world()
            return

        self.log.debug("Passing state to subprocess")
        self.passState()
        state = self.get_state()
        self.log.debug(state)
        #self.giveReward()
        self.log.debug("Getting chosen action back from subprocess")
        self.peek_future()
        self.get_action()
        self.log.debug("done")

    def chooseTarget(self):
        "Choose a new target for moving"
        self.sim.goal_x = random.randint(60,560)
        self.sim.goal_y = random.randint(80,360)

        self.sim.goal_x = 300 #rnd.randint(60,560)
        self.sim.goal_y = 180 #rnd.randint(80,360)
        self.sim.goal_orient = 2*pi*random.random() - pi

    def giveReward(self, state):
        if dist(state_pos(state), goal.pos) < 10:
            # Spend at most about 0.5 extra seconds correcting our orientation
            state_orient = state[4]
            reward = -0,5 * abs(goal.orientation - state_orient)/pi
            state.reward = reward
        else:
            state.reward = -1.0/dt

    def construct_state(self):
        state = ML.ML_pb2.WorldState()

        me = self.world.getSelf()
        state.robot.pos_x = me.pos[0]
        state.robot.pos_y = me.pos[1]
        state.robot.vel_x = me.velocity[0]
        state.robot.vel_y = me.velocity[1]
        state.robot.angle = me.orientation
        state.robot.ang_v = me.ang_v
        state.robot.left_angle = me.left_angle
        state.robot.right_angle = me.right_angle

        ball = self.world.getBall()
        state.ball.pos_x = ball.pos[0]
        state.ball.pos_y = ball.pos[1]
        state.ball.vel_x = ball.velocity[0]
        state.ball.vel_y = ball.velocity[1]

        # TODO: not working for some reason...
        # state.target.pos_x = self.sim.goal_x
        # state.target.pos_y = self.sim.goal_y
        # state.target.angle = self.sim.goal_orient

        return state

    def passState(self):
        "Tell the agent the current state of the world"
        state = self.construct_state()

        print >>self.p.stdin, state.SerializeToString()
        print >>self.p.stdin, "END"

    def get_action(self):
        line = self.getline()
        #print "STUFF:", line
        if line == 'RESET':
            return self.chooseTarget()

        params = line.split('|')
        self.log.info("PARAMS: " + str(params))
        self.eval_action(*map(int, params))

    def eval_action(self, driveL, driveR, steerL, steerR):
        self.drive_left(driveL)
        self.drive_right(driveR)
        self.macro_steer_left(steerL)
        self.macro_steer_right(steerR)
        #self.sendMessage()
