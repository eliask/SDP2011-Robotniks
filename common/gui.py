import cv
from utils import *
from math import *
import time
import logging
#from vision.camshift import CamShift
from vision.histogram import Histogram
import scipy.optimize
#from vision.histogram import Histogram

_fps = cv.Scalar(0,0,255,128)

class GUI:

    WindowName = 'Robotniks'
    images = {}
    active = 'standard'
    overlay = True
    histogram = True
    hist_visibility = 0.3
    Font = cv.InitFont(cv.CV_FONT_HERSHEY_SIMPLEX, 0.4, 0.4, 0, 1, 8)
    channel = 0 # display all channels by default
    quit = False
    curThreshold = 0
    thresholdAdjustment = False
    show_camshift = True

    def __init__(self, world, size, threshold):
        self.world = world

        self.threshold = threshold
        self.initThresholds()
        #self.camshift = CamShift()

        self.Ihist = cv.CreateImage((128,64), 8, 3);
        self.HSV       = cv.CreateImage(size, cv.IPL_DEPTH_8U, 3)
        self.R         = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)
        self.G         = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)
        self.B         = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)

        self.hist_image = None

        cv.NamedWindow(self.WindowName)
        self.drag_start = None
        cv.SetMouseCallback(self.WindowName, self.on_mouse)

    def initThresholds(self):
        T = self.threshold

        self.thresholds = \
            [ ("none", None, None),
              ("ball", T.ball, T.Tball),
              ("foreground", T.foreground, T.Tforeground),
              ("direction marker", T.dirmarker, T.Tdirmarker),
              ("yellow T", T.yellowT, T.Tyellow),
              ("blue T", T.blueT, T.Tblue),
              #("custom", T.custom, T.Tcustom),
              ("robots", T.robots, T.Trobots),
            ]

    def on_mouse(self, event, x, y, flags, param):
        if event == cv.CV_EVENT_LBUTTONDOWN:
            self.drag_start = (x, y)
        if event == cv.CV_EVENT_LBUTTONUP:
            self.drag_start = None
            self.track_window = self.selection
            self.autoThreshold()
        if self.drag_start:
            xmin = min(x, self.drag_start[0])
            ymin = min(y, self.drag_start[1])
            xmax = max(x, self.drag_start[0])
            ymax = max(y, self.drag_start[1])
            self.selection = (xmin, ymin, xmax - xmin, ymax - ymin)

    def autoThreshold(self):
        # self.hist_image = self.image
        # self.thresh_image = self.images['standard']

        #cv.SetImageROI(self.image, self.selection)
        #cv.ShowImage(self.WindowName, self.thresh_image)
        #cv.WaitKey(10)

        _histogram = Histogram(self.selection[2:])
        tmp = cv.CreateImage(self.selection[2:], 8,3)
        #cv.Copy(self.image, tmp)
        cv.CvtColor(self.images['foreground'], tmp, cv.CV_BGR2HSV)
        hist_props = _histogram.calcHistogram(tmp)
        B,G,R = hist_props
        ppB, ppG, ppR = map(lambda x:x['post_peaks'], hist_props)
        print ppB, ppG, ppR
        print hist_props

        self.threshold.Tyellow[1] = [0, 5+max(ppG, R[99]), 5+max(ppR, R[99])]
        self.threshold.Tyellow[2] = [255, 255, 255]

        cv.ResetImageROI(self.image)

        return

        start = time.time()
        minmax = self.threshold.Tforeground[1] + self.threshold.Tforeground[2]
        a= scipy.optimize.anneal( self.thresholdTarget, minmax,
                                  schedule='boltzmann',
                                  lower=[0,0,0,0,0,0],
                                  upper=[255,255,255,255,255,255] )
        # a= scipy.optimize.brute( self.thresholdTarget, minmax,
        #                           lower=[0,0,0,0,0,0],
        #                           upper=[255,255,255,255,255,255] )
        print "OUT:", a
        print "TIME:", time.time() - start
        #cv.ResetImageRoi(self.image)

    def getSelectionBorderArea(self, frame):
        S = self.selection
        thickness = 5
        top = (S[0], S[1], thickness, S[3])
        left = (S[0], S[1], S[2], thickness)
        right = (S[2]-thickness, S[1], thickness, S[3])
        bottom = (S[0], S[3]-thickness, S[2], thickness)

        area = 0
        cv.SetImageROI(frame, top)
        area += cv.CountNonZero(frame)
        cv.SetImageROI(frame, bottom)
        area += cv.CountNonZero(frame)
        cv.SetImageROI(frame, left)
        area += cv.CountNonZero(frame)
        cv.SetImageROI(frame, right)
        area += cv.CountNonZero(frame)

        return area

    def thresholdTarget(self, minmax):
        # Penalise bounds-crossing
        if (minmax < 0).any() or (minmax > 255).any():
            return 1e1000
        if (minmax[:3] > minmax[3:]).any():
            return 1e100

        self.threshold.Tyellow[1] = list(minmax[:3])
        self.threshold.Tyellow[2] = list(minmax[3:])
        print self.threshold.Tyellow
        out = self.threshold.yellowT(self.thresh_image)
        cv.SetImageROI(out, self.selection)
        cv.ShowImage(self.WindowName, out)
        cv.WaitKey(10)
        area_in = cv.CountNonZero(out)
        area_borders = self.getSelectionBorderArea(out)
        cv.ResetImageROI(out)
        #area_out = cv.CountNonZero(out)
        print area_in, area_borders
        return area_borders**2 - area_in**2

    def setFPS(self, startTime):
        self.fps = 1.0/(time.time() - startTime)

    def setActiveImage(self):
        self.image = self.images[self.active]

    def selectImageChannel(self):
        if self.image.nChannels == 3 and self.channel > 0:
            cv.Split(self.image, self.B, self.G, self.R, None)
            self.image = (self.B, self.G, self.R)[self.channel - 1]

    def applyThreshold(self):
        if self.curThreshold > 0 and self.image.nChannels == 3:
            name, thresh, vals = self.thresholds[self.curThreshold]
            logging.info("Thresholding image for: %s", name)
            print ("Thresholding image for: %s" % name)
            self.image = thresh(self.image)

    def draw(self, ents, startTime):
        self.setFPS(startTime)
        self.setActiveImage()
        self.selectImageChannel()
        self.applyThreshold()
        self.processInput()
        self.displayHistogram()
        self.displayOverlay(ents)
        #self.displayCamshift()
        self.drawMouseSelection()
        cv.ShowImage(self.WindowName, self.image)

    def drawMouseSelection(self):
        def is_rect_nonzero(r):
            (_,_,w,h) = r
            return (w > 0) and (h > 0)

        if self.drag_start and is_rect_nonzero(self.selection):
            sub = cv.GetSubRect(self.image, self.selection)
            save = cv.CloneMat(sub)
            cv.ConvertScale(self.image, self.image, 0.5)
            cv.Copy(save, sub)
            x,y,w,h = self.selection
            cv.Rectangle(self.image, (x,y), (x+w,y+h), (255,255,255))

            #cv.EllipseBox( self.image, track_box, cv.CV_RGB(255,0,0), 3, cv.CV_AA, 0 )
            # sel = cv.GetSubRect(self.hue, self.selection )
            # cv.CalcArrHist( [sel], hist, 0)
            # (_, max_val, _, _) = cv.GetMinMaxHistValue( hist)
            # if max_val != 0:
            #     cv.ConvertScale(hist.bins, hist.bins, 255. / max_val)

    def displayCamshift(self):
        self.camshift.run(self.image)

    def updateWindow(self, name, frame):
        self.images[name] = frame

    def switchWindow(self, name):
        self.active = name

    def displayOverlay(self, ents):
        if self.overlay:
            self.drawFPS()
            self.drawEntities(ents)

        if self.world.pointer:
            cv.Circle(self.frame, self.world.pointer,
                      20, cv.CV_RGB(0,255,255))

    def displayHistogram(self):
        self.hist_image = self.images['foreground']
        if self.histogram and self.image.nChannels == 3:
            try:
                if not self.hist_image:
                    self.hist_image = self.image
                self.drawHistogram(self.hist_image)
            except Exception, e:
                raise e
                logging.warn("drawHistogram failed: %s", e)

    def drawHistogram(self, image):
        w=0.5; n=9
        gauss1d = np.exp( -0.5 * w/n * np.array(range(-(n-1), n, 2))**2 )
        gauss1d /= sum(gauss1d)

        hist_size = 180
        hist = cv.CreateHist([hist_size], cv.CV_HIST_ARRAY, [[0,256]], 1)
        cv.CvtColor(image, self.HSV, cv.CV_BGR2HSV)
        cv.Split(self.HSV, self.B, self.G, self.R, None)

        channels = self.B, self.G, self.R
        _red   = cv.Scalar(255,0,0,0)
        _green = cv.Scalar(0,255,0,0)
        _blue  = cv.Scalar(0,0,255,0)
        _white = cv.Scalar(255,255,255,0)
        _trans = cv.Scalar(0,0,0,255)
        values = _blue, _green, _red

        positions = (0, (self.Ihist.height+10), 2*self.Ihist.height+20)

        for ch, colour, Y in zip(channels, values, positions):
            cv.CalcHist( [ch], hist, 0, None )
            cv.Set( self.Ihist, _trans)
            bin_w = cv.Round( float(self.Ihist.width)/hist_size )
            # min_value, max_value, pmin, pmax = cv.GetMinMaxHistValue(hist)

            X = self.HSV.width - self.Ihist.width
            rect = (X,Y,self.Ihist.width,self.Ihist.height)

            hist_arr = [cv.GetReal1D(hist.bins,i) for i in range(hist_size)]
            hist_arr = np.convolve(gauss1d, hist_arr, 'same')

            cv.SetImageROI(image, rect)
            hist_arr *= self.Ihist.height/max(hist_arr)
            for i,v in enumerate(hist_arr):
                cv.Rectangle( self.Ihist,
                              (i*bin_w, self.Ihist.height),
                              ( (i+1)*bin_w, self.Ihist.height - round(v) ),
                              colour, -1, 8, 0 )

            diffs = np.diff(hist_arr, 1)
            for i,v in enumerate(diffs):
                if v > 1 and diffs[i-1]*diffs[i] <= 0:
                    cv.Rectangle( self.Ihist,
                                  (i*bin_w, self.Ihist.height),
                                  ( (i+1)*bin_w, self.Ihist.height - round(hist_arr[i]) ),
                                  _white, -1, 8, 0 )

            cv.AddWeighted(image, 1-self.hist_visibility, self.Ihist,
                           self.hist_visibility, 0.0, image)

        cv.ResetImageROI(image)

    def drawRotBox(self, ent, color=cv.CV_RGB(255,128,0), label="UNNAMED"):
        if not ent:
            return
        if type(ent) == list and len(ent) > 0:
            ent = ent[0]
        x,y = map(int, entCenter(ent))
        radius = entDim(ent)[0]
        cv.Circle(self.image, (x,y), cv.Round(min(15,radius)), color)

        if 'orient' in ent and ent['orient']:
            o = ent['orient']
            cv.Circle(self.image, (x+50*cos(o), y+50*sin(o)),
                        cv.Round(min(15,radius)), cv.CV_RGB(200,200,200))

        rect = entRect(ent)
        cv.Rectangle( self.image, tuple(rectPos(rect)),
                      tuple(rectPos(rect) + rectSize(rect)),
                      color, 2, 8, 0 )

    def drawFPS(self):
        fps_pos = (10, 20)
        #fps_pos = (self.image.width - 70, self.image.height - 10)
        cv.PutText(self.image, "FPS: %d" % round(self.fps), fps_pos,
                   self.Font, _fps)

    def drawEntities(self, ents):
        #self.drawRotBox(ents['balls'], color=cv.CV_RGB(255,0,255), label='BALL')
        cv.Circle(self.image, tuple(self.world.getBall().pos),
                  15, (200,200,200))

        if ents['yellow']:
            logging.info( "Yellow robot at angle: %.3f",
                          robotAngle(ents['yellow']) )
            self.drawRotBox(ents['yellow'], color=cv.CV_RGB(255,255,64), label='YELLOW')
            self.drawRotBox(ents['yellow']['T'], color=cv.CV_RGB(200,200,64), label='YELLOW T')
            self.drawRotBox(ents['yellow']['dirmarker'],
                            color=cv.CV_RGB(255,255,0), label='YELLOW DIR')

        if ents['blue']:
            logging.info( "Blue robot at angle: %.3f",
                          robotAngle(ents['blue']) )
            self.drawRotBox(ents['blue'], color=cv.CV_RGB(64,64,255), label='BLUE')
            self.drawRotBox(ents['blue']['T'], color=cv.CV_RGB(200,64,255), label='BLUE T')
            self.drawRotBox(ents['blue']['dirmarker'],
                            color=cv.CV_RGB(255,255,0), label='BLUE DIR')

    def processInput(self):
        c = cv.WaitKey(5)
        k = chr(c % 0x100)

        if k == '\x1b': #ESC
            self.quit = True
        elif k == '\x09': #Tab
            # TODO: make toggleable threshold value adjustment trackbar
            self.thresholdAdjustment = not self.thresholdAdjustment
        elif k == 'r':
            self.switchWindow('raw')
        elif k == 'f':
            self.switchWindow('foreground')
        elif k == 'b':
            self.switchWindow('bgsub')
        elif k == 'm':
            self.switchWindow('mask')
        elif k == ' ':
            self.switchWindow('standard')
            self.curThreshold = 0
        elif k == 't':
            self.curThreshold = (self.curThreshold + 1) % len(self.thresholds)
        elif k == 'a':
            self.switchWindow('adaptive')
        # elif k == 'g':
        #     self.switchWindow('pyramid')
        elif k == '0':
            self.channel = 0
        elif k == '1':
            self.channel = 1
        elif k == '2':
            self.channel = 2
        elif k == '3':
            self.channel = 3
        elif k == 'o':
            self.overlay = not self.overlay
        elif k == 'h':
            self.histogram = not self.histogram
        elif k == '4':
            pass #self.show_camshift = not self.show_camshift
        elif k == 'q':
            #self.setTrackbars
            pass
        elif k == 'Q': # left arrow
            self.left()
        elif k == 'S': # right arrow
            self.right()
        elif k == 'R': # up arrow
            self.up()
        elif k == 'T': # down arrow
            self.right()
        elif k == 's':
            filename = time.strftime('%Y%m%d-%H%M-%S.png')
            cv.SaveImage(filename, self.image)
            logging.info("Screenshot saved at %s", filename)


