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
    :: CvMat -> ( [ (CvBox2D, CvRect) ], CvMat )

    Takes as input a grayscale image that should have some blobs in
    it. Outputs a data structure containing the 'centers' of the blobs
    and minimal rectangles enclosing them. A maximum of 3 blobs are
    returned.

    The input frame is modified in place.
    """
    contours, cstorage = get_contours(frame)
    out = draw_contours(frame, contours)

    candidates = []
    if contours is None:
        return ([], None)

    for c in contours.hrange():
        count = c.total
        #print 'Count:',count

        storage = cv.cvCreateMemStorage(0)
        min_box = cv.cvMinAreaRect2(c, storage)
        cv.cvReleaseMemStorage(storage)

        bounding_box = cv.cvBoundingRect(c, 0)

        candidates.append( (min_box, bounding_box) )

        area = getBoxArea(min_box)
        width = min(min_box.size.width, min_box.size.height)
        height = max(min_box.size.width, min_box.size.height)

        # print 'W:%.3f  H:%.3f  A:%.3f' % (width, height, area)
        # print "Angle:%.3f  Pos:(%.3f, %.3f)" % \
        #               (min_box.angle, min_box.center.x, min_box.center.y)

    cv.cvReleaseMemStorage(cstorage)
    candidates = sorted(candidates, key=lambda x:getBoxArea(x[0]), reverse=True)[:2]

    return candidates, out

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
