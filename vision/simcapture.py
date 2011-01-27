import cv

class SimCapture:

    def __init__(self, simulator):
        self.simulator = simulator

    def getFrame(self):
        return cv.LoadImage(self.simulator.visionFile)

