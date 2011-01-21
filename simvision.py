from simulator.simulator import *
import sys

sim = Simulator(vision=True, headless=sys.argv[-1] == 'headless')
sim.run()
