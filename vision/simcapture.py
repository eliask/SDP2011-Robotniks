from opencv import highgui

class SimCapture:

    def __init__(self, simulator):
        self.simulator = simulator

    def getFrame(self):
        return highgui.cvLoadImage(self.simulator.visionFile)

