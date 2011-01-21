from opencv import highgui

class SimCapture:

    def __init__(self, vision):
        self.vision = vision

    def getFrame(self):
        return highgui.cvLoadImage(self.vision.visionFile)

