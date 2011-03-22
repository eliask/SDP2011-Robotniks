import cv
from common.utils import *
import logging

def find_connected_components(frame):
    """Find connected components from an image.
    :: iplimage -> [ dict(box<CvBox2D>, rect<CvRect>) ]

    Takes as input a grayscale image that should have some blobs in
    it. Outputs a data structure containing the 'centers' of the blobs
    and minimal rectangles enclosing them. A maximum of 3 blobs are
    returned.

    The input frame is modified in place.
    """

    contours = get_contours(frame)
    #out = draw_contours(frame, contours)

    candidates = []
    for contour in contours:
        storage = cv.CreateMemStorage(0)
        minBox = cv.MinAreaRect2(contour, storage)

        boundingRect = cv.BoundingRect(contour, 0)
        candidates.append({ 'box' : minBox, 'rect' : boundingRect })

    candidates = sorted( candidates,
                         key=lambda x:getArea(x['box']),
                         reverse=True )
    return candidates

def get_contours(frame, approx=True):
    """Get contours from an image
    :: iplimage -> CvSeq
    """
    # A workaround for OpenCV 2.0 crash on receiving a (nearly) black image
    nonzero = cv.CountNonZero(frame)
    logging.debug("Segmentation got an image with %d nonzero pixels", nonzero)
    if nonzero < 20 or nonzero > 10000:
        return []

    storage = cv.CreateMemStorage(0)
    # find the contours
    contours = cv.FindContours( frame,
                                storage,
                                cv.CV_RETR_LIST,
                                cv.CV_CHAIN_APPROX_SIMPLE )
    if contours is None:
        return []

    res = []
    while contours:
        if not approx:
            result = contours
        else:
            result = cv.ApproxPoly( contours,
                                    storage,
                                    cv.CV_POLY_APPROX_DP,
                                    cv.ArcLength(contours)*0.02,
                                    1 )
        res.append( result )
        contours = contours.h_next()

    return res

_red = cv.Scalar(0, 0, 255, 0)
_green = cv.Scalar(0, 255, 0, 0)
contour_max_level=1

def draw_contours(frame, contours):
    out = cv.CreateImage(cv.GetSize(frame), cv.IPL_DEPTH_8U, 3)
    cv.CvtColor(frame, out, cv.CV_GRAY2BGR)

    # draw contours in red and green
    cv.DrawContours( out, contours,
                     _green,
                     _red,
                     contour_max_level,
                     1, #thickness
                     cv.CV_AA, #linetype
                     (0,0) )

    return out
