from common.utils import *
from math import *
import cv
import logging
import time
import threshold
import preprocess

class GUI:

    WindowName = 'Robotniks'
    images = {}
    active = 'standard'
    overlay = False
    histogram = False
    hist_visibility = 0.3
    Font = cv.InitFont(cv.CV_FONT_HERSHEY_SIMPLEX, 0.4, 0.4, 0, 1, 8)
    channel = 0 # display all channels by default
    quit = False
    curThreshold = 0
    thresholdAdjustment = False

    def __init__(self, world, size, threshold, vision):
        self.world = world
        self.threshold = threshold
        self.vision = vision

        self.Ihist = cv.CreateImage((128,64), 8, 3)
        self.HSV       = cv.CreateImage(size, cv.IPL_DEPTH_8U, 3)
        self.R         = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)
        self.G         = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)
        self.B         = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)

        self.hist_image = None

        cv.NamedWindow(self.WindowName)
        self.initThresholds()
        self.drag_start = None
        cv.SetMouseCallback(self.WindowName, self.on_mouse)
        self.scale = self.vision.pre.rawSize[0] / self.world.PitchLength

        self.toggle_overlay()

    def initThresholds(self):
        T = self.threshold

        dummy = ['tmp', [0,0,0], [0,0,0]]
        self.thresholds = \
            [ ("none", None, dummy),
              ("ball", T.ball, T.Tball),
              ("yellow T", T.yellowT, T.Tyellow),
              ("blue T", T.blueT, T.Tblue),
              ("dirmarker", T.dirmarker, T.Tdirmarker),
            ]

    def setCropRect(self, rect):
        self.vision.initComponents(rect)

    def restore_crop(self):
        self.vision.initComponents()

    def on_mouse(self, event, x, y, flags, param):
        if event == cv.CV_EVENT_LBUTTONDOWN:
            self.drag_start = (x,y)

        if event == cv.CV_EVENT_LBUTTONUP:
            self.drag_start = None
            self.track_window = self.selection
            if self.selection[2] > 600 and self.selection[3] > 300:
                self.setCropRect(self.selection)

        if self.drag_start:
            xmin = min(x, self.drag_start[0])
            ymin = min(y, self.drag_start[1])
            xmax = max(x, self.drag_start[0])
            ymax = max(y, self.drag_start[1])
            self.selection = (xmin, ymin, xmax - xmin, ymax - ymin)

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
            if self.thresholdAdjustment:
                threshold.updateValues()

            name, thresh, vals = self.thresholds[self.curThreshold]
            logging.info("Thresholding image for: %s", name)
            self.image = thresh(self.image)

            P = cv.GetSize(self.image)
            cv.PutText( self.image, "Threshold: %s" % name,
                        (P[0]-150,P[1]-20),
                        self.Font, (255,255,255,128) )

    def draw(self, ents, startTime):
        self.setFPS(startTime)
        self.setActiveImage()
        self.selectImageChannel()
        logging.debug("Applying threshold")
        self.applyThreshold()
        logging.debug("Processing input")
        self.processInput()
        logging.debug("Displaying overlay")
        self.displayHistogram()
        self.displayOverlay(ents)
        logging.debug("Showing image")
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

    def updateWindow(self, name, frame):
        self.images[name] = frame

    def switchWindow(self, name):
        if self.images[name]:
            self.active = name

    def displayOverlay(self, ents):
        if self.overlay:
            self.drawFPS()
            self.drawEntities(ents)

    def displayHistogram(self):
        self.hist_image = self.images['standard']
        if self.histogram and self.image.nChannels == 3:
            if not self.hist_image:
                self.hist_image = self.image
            self.drawHistogram(self.hist_image)

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
                                  ( (i+1)*bin_w,
                                    self.Ihist.height - round(hist_arr[i]) ),
                                  _white, -1, 8, 0 )

            cv.AddWeighted(image, 1-self.hist_visibility, self.Ihist,
                           self.hist_visibility, 0.0, image)

        cv.ResetImageROI(image)

    def draw_ent(self, ent, color=cv.CV_RGB(255,128,0) ):
        if not ent: return
        x,y = ent.pos
        radius = 30
        #cv.Circle(self.image, intPoint((x,y)), 8, color, -1)

        o = ent.orientation; D=30
        cv.Circle(self.image, intPoint((x+D*cos(o), y+D*sin(o))),
                  6, (200,200,200), -1)

    def drawFPS(self):
        cv.PutText( self.image, "FPS: %d" % round(self.fps), (10,20),
                    self.Font, (0,0,255,128) )

    def drawEntities(self, ents):
        pos = map(lambda x:self.scale*x, self.world.getBall().pos),
        cv.Circle( self.image, intPoint(self.world.getBall().pos),
                   10, (180,100,230), 2 )

        for robot, colour in [('blue', (230,100,100)), ('yellow', (0,200,200))]:
            robot = self.world.getRobot(robot)
            if robot:
                logging.info( "%s robot at angle: %.1f",
                              robot, degrees(robot.orientation))
                self.draw_ent(robot, colour)

    def change_threshold(self, delta):
        self.curThreshold = (self.curThreshold + delta) % len(self.thresholds)
        _, _, vals = self.thresholds[self.curThreshold]
        threshold.setValues(vals)

    def toggle_overlay(self):
        self.overlay = not self.overlay
        self.vision.featureEx.overlay = not self.vision.featureEx.overlay

    def processInput(self):
        #c = cv.WaitKey(500)
        c = cv.WaitKey(5)
        k = chr(c % 0x100)

        if k == 27: #ESC
            self.quit = True

        elif k == 's':
            filename = time.strftime('snapshots/%Y%m%d-%H%M%S.jpg')
            cv.SaveImage(filename, self.image)
            logging.info("Screenshot saved at %s", filename)

        elif k == '\x09': #Tab
            self.thresholdAdjustment = not self.thresholdAdjustment
            cv.DestroyWindow(self.WindowName)
            cv.NamedWindow(self.WindowName)

            threshold.trackbar_window = None
            if self.thresholdAdjustment:
                threshold.createTrackbars(self.WindowName)
        elif k == 't':
            self.change_threshold(1)

        elif k == 'o':
            self.toggle_overlay()
        elif k == 'h':
            self.histogram = not self.histogram

        elif k == 'q':
            self.restore_crop()
        elif k == 'r':
            self.switchWindow('raw')
        elif k == ' ':
            self.switchWindow('standard')
            self.curThreshold = 0

        elif k == '0':
            self.channel = 0
        elif k == '1':
            self.channel = 1
        elif k == '2':
            self.channel = 2
        elif k == '3':
            self.channel = 3

        elif k == 'Q': # left arrow
            self.change_threshold(-1)
        elif k == 'S': # right arrow
            self.change_threshold(1)
        elif k == 'R': # up arrow
            self.change_threshold(1)
        elif k == 'T': # down arrow
            self.change_threshold(-1)

