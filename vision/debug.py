import threshold
import cv

thresholds = {}

def thresholdValues(thresholdRec, gui):
    """Adds trackbars to the main window for adjusting thresholding values

    Optionally uses some other window (specified by 'window').
    """

    def set1a(x): thresholdRec[1][0]=x
    def set2a(x): thresholdRec[1][1]=x
    def set3a(x): thresholdRec[1][2]=x
    def set1z(x): thresholdRec[2][0]=x
    def set2z(x): thresholdRec[2][1]=x
    def set3z(x): thresholdRec[2][2]=x

    cv.CreateTrackbar("ch1 min", gui.WindowName, thresholdRec[1][0], 255, set1a)
    cv.CreateTrackbar("ch2 min", gui.WindowName, thresholdRec[1][1], 255, set2a)
    cv.CreateTrackbar("ch3 min", gui.WindowName, thresholdRec[1][2], 255, set3a)

    cv.CreateTrackbar("ch1 max", gui.WindowName, thresholdRec[2][0], 255, set1z)
    cv.CreateTrackbar("ch2 max", gui.WindowName, thresholdRec[2][1], 255, set2z)
    cv.CreateTrackbar("ch3 max", gui.WindowName, thresholdRec[2][2], 255, set3z)
