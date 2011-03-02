from strategy import *

# The non-acting AI. Could be used for dummy targets or for human control
class Null(Strategy):
    def __init__(self, *args):
        Strategy.__init__(self, *args, name='null')

    def run(self):
        pass
