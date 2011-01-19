from opencv import cv
from utils import *

_red = cv.cvScalar(0, 0, 255, 0);
_green = cv.cvScalar(0, 255, 0, 0);

# Object areas for each entity
Aball = (80,180) #120..140 seems typical
Arobot = (2000,4000) # 2900..3000 seems typical

contour_max_level=1
contour_min_area=200

def find_connected_components(frame):
    """Find connected components from an image.
    :: CvMat -> [ dict(box<CvBox2D>, rect<CvRect>) ]

    Takes as input a grayscale image that should have some blobs in
    it. Outputs a data structure containing the 'centers' of the blobs
    and minimal rectangles enclosing them. A maximum of 3 blobs are
    returned.

    The input frame is modified in place.
    """
    contours, cstorage = get_contours(frame)
    #out = draw_contours(frame, contours)

    candidates = []
    if contours is None:
        return []

    for c in contours.hrange():
        storage = cv.cvCreateMemStorage(0)
        minBox = cv.cvMinAreaRect2(c, storage)
        cv.cvReleaseMemStorage(storage)

        boundingRect = cv.cvBoundingRect(c, 0)
        candidates.append({ 'box' : minBox, 'rect' : boundingRect })

    cv.cvReleaseMemStorage(cstorage)
    candidates = sorted(candidates, key=lambda x:getBoxArea(x['box']), reverse=True)

    return candidates

def get_contours(frame):
    """Get contours from an image
    :: CvMat -> ( CvTypedSeq<CvPoint>, CvCvMemStorage )
    """
    storage = cv.cvCreateMemStorage(0)
    # find the contours
    nb_contours, contours = \
        cv.cvFindContours( frame,
                           storage,
                           cv.sizeof_CvContour,
                           cv.CV_RETR_LIST,
                           cv.CV_CHAIN_APPROX_SIMPLE,
                           cv.cvPoint(0, 0) )

    if contours is None:
        return None, storage

    contours = cv.cvApproxPoly( contours,
                                cv.sizeof_CvContour,
                                storage,
                                cv.CV_POLY_APPROX_DP,
                                cv.cvContourPerimeter(contours)*0.02,
                                1 )

    # print 'Num:',nb_contours
    # print type(contours), dir(contours)
    return contours, storage

def draw_contours(frame, contours):
    out = cv.cvCreateImage(cv.cvGetSize(frame), cv.IPL_DEPTH_8U, 3)
    cv.cvCvtColor(frame, out, cv.CV_GRAY2BGR)

    # draw contours in red and green
    cv.cvDrawContours( out, contours,
                       _green, _red,
                       contour_max_level,
                       1,
                       cv.CV_AA,
                       cv.cvPoint(5, 5) )

    return out
