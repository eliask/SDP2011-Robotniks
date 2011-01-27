import cv
from utils import *
from math import *
import time
import logging

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

    def __init__(self, world, size, threshold):
        self.world = world

        self.threshold = threshold
        self.initThresholds()

        self.Ihist = cv.CreateImage((128,64), 8, 3);
        self.R         = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)
        self.G         = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)
        self.B         = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)

        cv.NamedWindow(self.WindowName)

    def initThresholds(self):
        T = self.threshold
        self.thresholds = \
            [ ("none", None, None),
              ("foreground", T.foreground, T.Tforeground),
              ("robots", T.robots, T.Trobots),
              ("ball", T.ball, T.Tball),
              ("blue T", T.blueT, T.Tblue),
              ("yellow T", T.yellowT, T.Tyellow),
              ("direction marker", T.dirmarker, T.Tdirmarker),
            ]

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
            self.image = thresh(self.image)

    def draw(self, ents, startTime):
        self.setFPS(startTime)
        self.setActiveImage()
        self.selectImageChannel()
        self.applyThreshold()
        self.processInput()
        self.displayHistogram()
        self.displayOverlay(ents)
        cv.ShowImage(self.WindowName, self.image)

    def updateWindow(self, name, frame):
        self.images[name] = frame

    def switchWindow(self, name):
        self.active = name

    def displayOverlay(self, ents):
        if self.overlay:
            try:
                self.drawFPS()
                self.drawEntities(ents)
            except Exception, e:
                logging.warn("overlay drawing failed: %s", e)

        if self.world.pointer:
            cv.Circle(self.frame, self.world.pointer,
                      cv.Round(20), cv.CV_RGB(0,255,255))

    def displayHistogram(self):
        if self.histogram and self.image.nChannels == 3:
            try:
                self.drawHistogram()
            except Exception, e:
                logging.warn("drawHistogram failed: %s", e)

    def drawHistogram(self):
        hist_size = 64
        hist = cv.CreateHist([hist_size], cv.CV_HIST_ARRAY, [[0,256]], 1)
        cv.Split(self.image, self.B, self.G, self.R, None)

        channels = self.B, self.G, self.R
        _red   = cv.Scalar(255,0,0,0)
        _green = cv.Scalar(0,255,0,0)
        _blue  = cv.Scalar(0,0,255,0)
        _trans = cv.Scalar(0,0,0,255)
        values = _blue, _green, _red

        positions = (0, (self.Ihist.height+10), 2*self.Ihist.height+20)

        for ch, colour, Y in zip(channels, values, positions):
            cv.CalcHist( [ch], hist, 0, None )
            cv.Set( self.Ihist, _trans)
            bin_w = cv.Round( float(self.Ihist.width)/hist_size )

            min_value, max_value, pmin, pmax = cv.GetMinMaxHistValue(hist)
            cv.Scale( hist.bins, hist.bins,
                      float(self.Ihist.height)/max_value, 0 )

            X = self.image.width - self.Ihist.width
            rect = (X,Y,self.Ihist.width,self.Ihist.height)
            cv.SetImageROI(self.image, rect)

            for i in range(hist_size):
                cv.Rectangle( self.Ihist,
                              (i*bin_w, self.Ihist.height),
                              ( (i+1)*bin_w, self.Ihist.height
                                - cv.Round(cv.GetReal1D(hist.bins,i)) ),
                              colour, -1, 8, 0 );

            cv.AddWeighted(self.image, 1-self.hist_visibility, self.Ihist,
                           self.hist_visibility, 0.0, self.image)

        cv.ResetImageROI(self.image)

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
        self.drawRotBox(ents['balls'], color=cv.CV_RGB(255,0,255), label='BALL')

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

        try:
            k = chr(c)
        except ValueError, e:
            logging.debug(e)
            return

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
            self.threshold = self.thresholds[self.curThreshold]
        # elif k == 'a':
        #     self.switchWindow('adaptive')
        # elif k == 'g':
        #     self.switchWindow('pyramid')
        elif k == '0':
            self.channel = 1
        elif k == '1':
            self.channel = 1
            print "CHAN"
        elif k == '2':
            self.channel = 2
        elif k == '3':
            self.channel = 3
        elif k == 'o':
            self.overlay = not self.overlay
        elif k == 'h':
            self.histogram = not self.histogram
        elif k == 'q':
            #self.setTrackbars
            pass
        elif k == 's':
            filename = time.strftime('%Y%m%d-%H%M-%S.png')
            cv.SaveImage(filename, self.image)
            logging.info("Screenshot saved at %s", filename)


