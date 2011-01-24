import threshold
from opencv import highgui

def thresholdValues(thresholdRec, window='Camera'):
    """Adds trackbars to the main window for adjusting thresholding values

    Optionally uses some other window (specified by 'window').
    """

    def set1a(x): thresholdRec[1][0]=x
    def set2a(x): thresholdRec[1][1]=x
    def set3a(x): thresholdRec[1][2]=x
    def set1z(x): thresholdRec[2][0]=x
    def set2z(x): thresholdRec[2][1]=x
    def set3z(x): thresholdRec[2][2]=x

    highgui.cvCreateTrackbar("ch1 min", window, thresholdRec[1][0], 255, set1a)
    highgui.cvCreateTrackbar("ch2 min", 'Camera', thresholdRec[1][1], 255, set2a)
    highgui.cvCreateTrackbar("ch3 min", 'Camera', thresholdRec[1][2], 255, set3a)

    highgui.cvCreateTrackbar("ch1 max", 'Camera', thresholdRec[2][0], 255, set1z)
    highgui.cvCreateTrackbar("ch2 max", 'Camera', thresholdRec[2][1], 255, set2z)
    highgui.cvCreateTrackbar("ch3 max", 'Camera', thresholdRec[2][2], 255, set3z)

def window(name, frame):
    highgui.NamedWindow(name)
    highgui.cvShowImage(name, frame)
