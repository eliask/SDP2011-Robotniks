import cv
from common.utils import *
import logging

_red = cv.Scalar(0, 0, 255, 0)
_green = cv.Scalar(0, 255, 0, 0)

# Object areas for each entity
Aball = (80,180) #120..140 seems typical
Arobot = (2000,4000) # 2900..3000 seems typical

contour_max_level=1
contour_min_area=200

def find_connected_components(frame):
    """Find connected components from an image.
    :: iplimage -> [ dict(box<CvBox2D>, rect<CvRect>) ]

    Takes as input a grayscale image that should have some blobs in
    it. Outputs a data structure containing the 'centers' of the blobs
    and minimal rectangles enclosing them. A maximum of 3 blobs are
    returned.

    The input frame is modified in place.
    """

    # A workaround for OpenCV 2.0 crash on receiving a (nearly) black image
    nonzero = cv.CountNonZero(frame)
    if nonzero < 20:
        return []
    logging.debug("Segmentation got an image with %d nonzero pixels", nonzero)

    contours = get_contours(frame)
    #out = draw_contours(frame, contours)

    if contours is None:
        return []

    candidates = []
    while contours:
        storage = cv.CreateMemStorage(0)
        minBox = cv.MinAreaRect2(contours, storage)

        boundingRect = cv.BoundingRect(contours, 0)
        candidates.append({ 'box' : minBox, 'rect' : boundingRect })

        contours = contours.h_next()

    candidates = sorted( candidates,
                         key=lambda x:getArea(x['box']),
                         reverse=True )
    return candidates

def get_contours(frame):
    """Get contours from an image
    :: iplimage -> CvSeq
    """
    storage = cv.CreateMemStorage(0)
    # find the contours
    contours = cv.FindContours( frame,
                                storage,
                                cv.CV_RETR_LIST,
                                cv.CV_CHAIN_APPROX_SIMPLE )
    if contours is None:
        return

    contours = cv.ApproxPoly( contours,
                              storage,
                              cv.CV_POLY_APPROX_DP,
                              cv.ArcLength(contours)*0.05,
                              1 )
    return contours

def draw_contours(frame, contours):
    out = cv.CreateImage(cv.GetSize(frame), cv.IPL_DEPTH_8U, 3)
    cv.CvtColor(frame, out, cv.CV_GRAY2BGR)

    # draw contours in red and green
    cv.DrawContours( out, contours,
                       _green, _red,
                       contour_max_level,
                       1,
                       cv.CV_AA,
                       cv.Point(5, 5) )

    return out
