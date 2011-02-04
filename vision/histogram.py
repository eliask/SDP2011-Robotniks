import cv
import numpy as np

_red   = cv.Scalar(255,0,0,0)
_green = cv.Scalar(0,255,0,0)
_blue  = cv.Scalar(0,0,255,0)
_white = cv.Scalar(255,255,255,0)
_trans = cv.Scalar(0,0,0,255)

class Histogram:

    hist_size = 120
    hist_visibility = 0.3

    def __init__(self, size):
        w=0.5; n=9
        self.gauss1d = np.exp( -0.5 * w/n * np.array(range(-(n-1), n, 2))**2 )
        self.gauss1d /= sum(self.gauss1d)
        self.hist = cv.CreateHist([self.hist_size], cv.CV_HIST_ARRAY, [[0,256]], 1)

        self.Ihist = cv.CreateImage((128,64), 8, 3)
        self.R         = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)
        self.G         = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)
        self.B         = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)

    def smoothHistogram(self):
        hist_arr = [cv.GetReal1D(self.hist.bins,i) for i in range(self.hist_size)]
        hist_arr = np.convolve(self.gauss1d, hist_arr, 'same')
        return hist_arr

    def calcHistogram(self, image):
        cv.Split(image, self.B, self.G, self.R, None)
        channels = self.B, self.G, self.R
        plateaus = []
        for chnum, ch in enumerate(channels):
            #, colour, Ypos in zip(channels, values, positions):
            cv.CalcHist( [ch], self.hist, 0, None )

            hist_arr = self.smoothHistogram()
            diffs = np.diff(hist_arr, 1)
            plateaus.append([])
            for i,v in enumerate(diffs):
                if hist_arr[i] > 1 and diffs[i-1]*diffs[i] <= 0:
                    plateaus[chnum].append(i)

            # for i in plateaus[chnum]:
            #     if i > 10 and min_val

            #self.drawHistogram(image, chnum, hist_arr, plateaus)

        return plateaus

    def drawHistogram(self, image, chnum, hist_arr, plateaus):
        positions = (0, (self.Ihist.height+10), 2*self.Ihist.height+20)
        colour_values = _blue, _green, _red
        colour = colour_values[chnum]
        Y = positions[chnum]

        cv.Set( self.Ihist, _trans)
        bin_w = cv.Round( float(self.Ihist.width)/self.hist_size )
        # min_value, max_value, pmin, pmax = cv.GetMinMaxHistValue(hist)

        X = image.width - self.Ihist.width
        rect = (X,Y,self.Ihist.width,self.Ihist.height)

        cv.SetImageROI(image, rect)
        scaling = self.Ihist.height/max(hist_arr)
        hist_arr *= scaling
        for i,v in enumerate(hist_arr):
            cv.Rectangle( self.Ihist,
                          (i*bin_w, self.Ihist.height),
                          ( (i+1)*bin_w, self.Ihist.height - round(v) ),
                          colour, -1, 8, 0 )

        for i in plateaus[chnum]:
            cv.Rectangle( self.Ihist,
                          (i*bin_w, self.Ihist.height),
                          ( (i+1)*bin_w, self.Ihist.height - round(hist_arr[i]) ),
                          _white, -1, 8, 0 )

        cv.AddWeighted(image, 1-self.hist_visibility, self.Ihist,
                       self.hist_visibility, 0.0, image)

        cv.ResetImageROI(image)

