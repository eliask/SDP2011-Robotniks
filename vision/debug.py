import threshold
from opencv import highgui

thresholds = {}

def update(frame):
    for window, f in thresholds.items():
        highgui.cvShowImage(window, f(frame))

def thresholdValues(thresholdRec, thresholdFn, window='Camera'):
    """Adds trackbars to the main window for adjusting thresholding values

    Optionally uses some other window (specified by 'window').
    """

    def set1a(x): thresholdRec[1][0]=x
    def set2a(x): thresholdRec[1][1]=x
    def set3a(x): thresholdRec[1][2]=x
    def set1z(x): thresholdRec[2][0]=x
    def set2z(x): thresholdRec[2][1]=x
    def set3z(x): thresholdRec[2][2]=x

    highgui.cvNamedWindow(window)
    highgui.cvCreateTrackbar(window+"ch1 min", window, thresholdRec[1][0], 255, set1a)
    highgui.cvCreateTrackbar(window+"ch2 min", window, thresholdRec[1][1], 255, set2a)
    highgui.cvCreateTrackbar(window+"ch3 min", window, thresholdRec[1][2], 255, set3a)

    highgui.cvCreateTrackbar(window+"ch1 max", window, thresholdRec[2][0], 255, set1z)
    highgui.cvCreateTrackbar(window+"ch2 max", window, thresholdRec[2][1], 255, set2z)
    highgui.cvCreateTrackbar(window+"ch3 max", window, thresholdRec[2][2], 255, set3z)

    thresholds[window] = thresholdFn
