import pygame, sys, random
from opencv import cv, highgui
from features import FeatureExtraction
import segmentation
import threshold
from preprocess import Preprocessor
from utils import *

# goalDim = (60, 18)
# robotDim = (20,18)
# pitchDim = (244, 122)

g_capture = None
g_slider_pos = 0

winMap = {}
def updateWin(name, frame):
    if not winMap.has_key(name):
        winMap[name] = \
        {'window' : highgui.cvNamedWindow(name, highgui.CV_WINDOW_AUTOSIZE)}
    highgui.cvShowImage(name, frame)

def updateTrackbar(name, window_name):
    if not winMap.has_key(name):
        raise NameError, "No such window:", window_name
    elif not WinMap[name].has_key('trackbar'):
        WinMap[name] = \
        {'trackbar' : highgui.cvCreateTrackbar(
                name, window_name, g_slider_pos, frames, on_trackbar)}


Xbgr=[35,10,20]
def setB(x): Xbgr[0]=x
def setG(x): Xbgr[1]=x
def setR(x): Xbgr[2]=x

# def setFA(x): features.params[0]=x
# def setFB(x): features.params[0]=x

F = FeatureExtraction( (768, 576) )

def gotoFrame(pos):
    highgui.cvSetCaptureProperty(g_capture, highgui.CV_CAP_PROP_POS_FRAMES, pos)
    print "Pos:", highgui.cvGetCaptureProperty(g_capture, highgui.CV_CAP_PROP_POS_FRAMES)

def bar():
    # create windows
    # highgui.cvNamedWindow('Raw', highgui.CV_WINDOW_AUTOSIZE)
    # highgui.cvNamedWindow('Adaptive threshold', highgui.CV_WINDOW_AUTOSIZE)
    # highgui.cvNamedWindow('Threshold', highgui.CV_WINDOW_AUTOSIZE)

    # create capture device
    #g_capture = cvCreateCameraCapture(-1)
    g_capture = highgui.cvCreateFileCapture(sys.argv[-1])
    highgui.cvSetCaptureProperty(g_capture,
                                 highgui.CV_CAP_PROP_FRAME_WIDTH, 768)
    highgui.cvSetCaptureProperty(g_capture,
                                 highgui.CV_CAP_PROP_FRAME_HEIGHT, 512)

    frames = highgui.cvGetCaptureProperty(g_capture,
                                          highgui.CV_CAP_PROP_FRAME_COUNT)

    gotoFrame(215)

    # print FPS
    print 'FPS:', \
        highgui.cvGetCaptureProperty(g_capture, highgui.CV_CAP_PROP_FPS)

    if not g_capture:
        print "Error opening g_capture device"
        sys.exit(1)

    size = cv.cvSize(768, 576)
    num_chans = 3
    chsv = [ cv.cvCreateImage(size, cv.IPL_DEPTH_8U, 1)
             for _ in range(num_chans) ]
    cbgr = [ cv.cvCreateImage(size, cv.IPL_DEPTH_8U, 1)
             for _ in range(num_chans) ]

    eig_image = cv.cvCreateMat(size.height, size.width, cv.CV_32FC1)
    temp_image = cv.cvCreateMat(size.height, size.width, cv.CV_32FC1)

    gray = cv.cvCreateImage(size, cv.IPL_DEPTH_8U, 1)
    Iavg = cv.cvCreateImage(size, cv.IPL_DEPTH_8U, 3)
    IGD = cv.cvCreateImage(size, cv.IPL_DEPTH_8U, 3)
    bg = highgui.cvLoadImage('background.png')
    # Roughly keeps the lightness constant across the pitch.
    # i.e. the robot won't suddenly become much lighter, etc.
    #cv.cvConvertScale(bg2,bg2,0.6,0)
    ground_mask = highgui.cvLoadImage('ground_mask.png')
    #bgSidesMask = highgui.cvLoadImage('bg_sides_mask.png')
    pitch_mask = highgui.cvLoadImage('pitch_mask.png')

    # bg2 = cv.cvCreateImage(size, cv.IPL_DEPTH_8U, 3)
    # cv.cvZero(bg2)
    #cv.cvAnd(bg, ground_mask, bg)
    #cv.cvAnd(bg, pitch_mask, bg2)
    #cv.cvSub(bg, bg2, bg2)

    # updateWin("X", bg)
    # highgui.cvCreateTrackbar("R", 'X', Xbgr[2], 255, setR)
    # highgui.cvCreateTrackbar("G", 'X', Xbgr[1], 255, setG)
    # highgui.cvCreateTrackbar("B", 'X', Xbgr[0], 255, setB)

    # updateWin("Contour", bg)
    # # highgui.cvCreateTrackbar("A", 'Contour', Features.contour_min_area, 800, setFA)
    # # highgui.cvCreateTrackbar("B", 'Contour', Features.B, 30, setFB)

    # updateWin("Hough", bg)
    # highgui.cvCreateTrackbar("param1", 'Hough', features.params[0], 500, setFA)
    # highgui.cvCreateTrackbar("param2", 'Hough', features.params[1], 500, setFB)

    Iobj = cv.cvCreateImage(size, cv.IPL_DEPTH_8U, 3)
    Imask = cv.cvCreateImage(size, cv.IPL_DEPTH_8U, 3)
    pIat = cv.cvCreateImage(size, cv.IPL_DEPTH_8U, 1)
    Iopen = cv.cvCreateImage(size, cv.IPL_DEPTH_8U, 1)
    Iclose = cv.cvCreateImage(size, cv.IPL_DEPTH_8U, 1)

    pre=Preprocessor(cv.cvSize(768, 576))

    pause=False
    frame=None
    n=0
    while True:
        # capture the current frame
        if not pause:
            #Use something like this for, say, averaging a pic
            #frame = highgui.cvLoadImage('train/%08d.png' % n)

            frame = highgui.cvQueryFrame(g_capture)
            if frame is None: break
            cv.cvAnd(frame, pitch_mask, frame)

        print "Frame:",n
        n+=1

        #size = cv.cvGetSize(frame)

        ########################################
        cv.cvCvtColor(frame, gray, cv.CV_BGR2GRAY)

        ########################################
        # Ignore potentially distracting things outside the pitch
        # updateWin('BG', bg)
        # updateWin('BG2', bg2)

        ########################################
        #TODO: how to make this work with python?
        #cv.cvSetImageROI(frame, cv.cvRect(0,50,768,450))

        ########################################
        #center = cv.cvPoint(random.randrange(1,768), random.randrange(1,512))
        #cv.cvCircle(frame, center, 15, cv.CV_BGR(300,1,1))

        ########################################
        updateWin('Raw', frame)
        # if frames > 0:
        #     updateTrackbar("Position", "Raw")

        ########################################
        #updateWin('Corrected', Preprocessor.undistort(frame))

        ########################################
        kernel = cv.cvCreateStructuringElementEx(5, 5,
                                                 2,2, #X,Y offsets
                                                 cv.CV_SHAPE_RECT)

        cv.cvSub(frame, bg, Imask)
        #updateWin('Background subtraction', Imask)
        gray = threshold.foreground(Imask)
        cv.cvCvtColor(gray, Imask, cv.CV_GRAY2BGR)

        #Enlarge the mask a bit to account eliminate missing parts due to noise
        cv.cvDilate(Imask, Imask)
        #This step essentially just reduces the amount of noise
        cv.cvMorphologyEx(Imask, Imask, None, kernel, cv.CV_MOP_OPEN)
        cv.cvMorphologyEx(Imask, Imask, None, kernel, cv.CV_MOP_CLOSE)
        #updateWin('Y', Iobj)
        cv.cvAnd(Imask, frame, Iobj)
        updateWin('X', Iobj)

        #updateWin('Backplate', threshold.backplate(Iobj))
        #updateWin('Direction marker', threshold.dirmarker(Iobj))
        mask2 = threshold.dirmarker(Iobj)
        cv.cvCvtColor(mask2, Imask, cv.CV_GRAY2BGR)
        #updateWin('Hough', features.detect_dirmarker(Imask))
        #robot_positions, o = segmentation.find_connected_components(gray)
        ballmask = threshold.ball(Iobj)
        #updateWin('Ball', ballmask)

        # pos = {}

        # pos['ball'], oball = \
        #     segmentation.find_connected_components(ballmask)

        # yellow_mask = threshold.yellowTAndBall(Iobj)
        # #updateWin('Yellow', threshold.yellowT(Iobj)) #also includes the ball; xor?
        # #updateWin('Yellow,ball', yellow_mask) #threshold.yellowTAndBall(Iobj)
        # pos['yellow'], oyellow = \
        #     segmentation.find_connected_components(yellow_mask)
        # # updateWin('Yellow2', oyellow)

        blue_mask = threshold.blueT(Iobj)
        updateWin('Blue', threshold.blueT(Iobj)) #works
        # pos['blue'] = \
        #     segmentation.find_connected_components(blue_mask)

        # updateWin('Yellow', Features.threshold(Iavg, Features.Tyellow))
        # updateWin('Yellow orig', Features.threshold(frame, Features.Tyellow))
        #updateWin('Ball orig', Features.threshold(frame, Features.Tball))
        #updateWin('Yellow orig', Features.threshold(frame, Features.Tyellow))

        # Finds the approximate position of each object with little noise
        # The approximation should later be refined by some method
        #cv.cvMorphologyEx(IGD, IGD, None, kernel, cv.CV_MOP_OPEN)
        #cv.cvMorphologyEx(IGD, IGD, None, kernel, cv.CV_MOP_CLOSE)
        #updateWin('X', IGD)

        # It = cv.cvCreateImage(size, cv.IPL_DEPTH_8U, 1)
        # cv.cvCvtColor(IGD, It, cv.CV_BGR2GRAY)
        # cv.cvThreshold(It, It, 1, 255, cv.CV_THRESH_BINARY)
        # cv.cvCvtColor(It, IGD, cv.CV_GRAY2BGR)
        # cv.cvAnd(IGD, frame, IGD)

        # cv.cvCvtColor(Iobj, gray, cv.CV_BGR2GRAY)
        # #cv.cvDilate(gray, gray)
        # #updateWin('X', gray)
        # pos['robots'], ostuff = \
        #     segmentation.find_connected_components(gray)

        # for o in pos.values():
        #     for box2d, rect in o:
        #         x,y = BoxCenterPos(box2d)
        #         radius = box2d.size.width
        #         cv.cvCircle(Iobj, Point(x, y), cv.cvRound(min(30,radius)),
        #                     cv.CV_RGB(random.randint(1,255),
        #                               random.randint(1,255),
        #                               random.randint(1,255)) )

        # updateWin('Bar', Iobj)

        # o=Segmenter.segment(Features.threshold(frame, Features.Tblue), 'Blue')
        # print o

        ########################################

        # hsv = cv.cvCreateImage(size, cv.IPL_DEPTH_8U, 3)
        # cv.cvCvtColor(frame, hsv, cv.CV_BGR2HSV)
        # cv.cvSplit(hsv, chsv[0], chsv[1], chsv[2], None)
        # updateWin('Hue', chsv[0])
        # updateWin('Saturation', chsv[1])
        # updateWin('Value', chsv[2])

        ########################################
        # bgr = cv.cvCloneImage(frame)
        # cv.cvSplit(bgr, cbgr[0], cbgr[1], cbgr[2], None)
        # updateWin('Blue', cbgr[0])
        # updateWin('Green', cbgr[1])
        # updateWin('Red', cbgr[2])

        ########################################
        # N=n-665
        # cv.cvAddWeighted(frame, 1.0/(N+1), Iavg, N/(N+1.0), 0, Iavg)
        # print 1.0/(N+1), N/(N+1.0)
        # updateWin('Average', Iavg)
        # n=n+1

        ########################################
        #It = cv.cvCreateImage(size, cv.IPL_DEPTH_8U, 1)
        #cv.cvThreshold(c[2], It, 200, 100, cv.CV_THRESH_BINARY_INV)
        # updateWin('backplate', Features.threshold(frame, Features.Tbackplate))
        # updateWin('ball', Features.threshold(frame, Features.Tball))
        # updateWin('blue', Features.threshold(frame, Features.Tblue))

        ########################################
        # cv.cvSmooth(IGD, Imask, cv.CV_GAUSSIAN, 11)
        # cv.cvSub(IGD, Imask, Imask)
        # updateWin('Gaussian diff', Imask)

        ########################################
        Tsides = ( 'bgr', (100,  100,  100), (255, 255, 255) )
        # sides = Features.threshold(Iavg, Tsides)
        # updateWin('Sides', sides)
        # cv.cvSmooth(Iavg, IGD, cv.CV_GAUSSIAN, 11)
        # cv.cvSub(Iavg, IGD, IGD)
        #cv.cvAdd(IGD,Imask,IGD)
        #cv.cvCvtColor(IGD, gray, cv.CV_BGR2GRAY)
        # cv.cvAdaptiveThreshold(gray, gray, 255, cv.CV_ADAPTIVE_THRESH_MEAN_C,
        #                        cv.CV_THRESH_BINARY_INV, 9, 9)
        # updateWin('Gaussian diff 2', IGD)

        ########################################
        # cv.cvAdaptiveThreshold(gray, Iat, 255, cv.CV_ADAPTIVE_THRESH_MEAN_C,
        #                        cv.CV_THRESH_BINARY_INV, 5, 5)
        #updateWin("Adaptive thresholding", Iat)

        #Combine GaussDiff with adaptive thresholding and original
        # cv.cvCvtColor(Iat, IGD, cv.CV_GRAY2BGR)
        # cv.cvAddWeighted(frame, 1/8.0, Imask, 2.0, 0, Imask)
        # #cv.cvAddWeighted(Imask, 2/3.0, IGD, 1.0, 0, Imask)
        # updateWin("Combo", Imask)

        ########################################

        # cv.cvCanny(gray, Iat, 0, 9, 3)
        # updateWin("Canny", Iat)

        # kernel = cv.cvCreateStructuringElementEx(3,3,1,1,cv.CV_SHAPE_RECT)
        #cv.cvMorphologyEx(gray, Iopen, None, kernel, cv.CV_MOP_OPEN)

        # cv.cvCvtColor(Iobj, gray, cv.CV_BGR2GRAY)
        # for (x,y) in cv.GoodFeaturesToTrack(img, eig_image, temp_image, 10, 0.04, 1.0, useHarris = True):
        #     print "good feature at", x,y

        # handle events
        k = highgui.cvWaitKey(5)

        # processing depending on the character
        if k == 'p':
            pause=not pause

        if k == 0x1b:
            print 'ESC pressed. Exiting ...'
            break

    #Iavg = cv.cvCreateImage(size, cv.IPL_DEPTH_32S, 3)
    #highgui.cvShowImage('Raw', Iavg)
    #highgui.cvSaveImage("avg.png", Iavg)
    bar() # Loop
    #highgui.cvDestroyAllWindows()

if __name__ == "__main__":
    bar()
