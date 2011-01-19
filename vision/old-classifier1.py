    def getBoxes(struct):
        return [ x[0] for x in struct ]

    def getSize(box):
        width = min(box.size.width, box.size.height)
        height = max(box.size.width, box.size.height)
        return width, height

    # First filter features by size
    for oBox in getBoxes(pos['objects']):
        sizeMatch

    # Then match direction markers to robots


def classifyBySize(pos):
    for name in Sizes.keys():
        if sizeMatch(obj, name):
            ents[

def sizeMatch(obj, name):
    width, height = getSize(obj)

    if  Sizes[name][0] < width  < Sizes[name][1] \
    and Sizes[name][2] < height < Sizes[name][3]:
        return True
    else:
        return False



def classify1(pos):
    entities = {}
    for name in ['yellow', 'blue', 'ball']:
        entities[name] = Entity(None, None, 1000)

    def getBoxes(struct):
        return [ x[0] for x in struct ]
    def getClosest(theBox, name):
        boxes = [x for x in getBoxes(pos[name]) if sizeMatch(x, name)]
        if len(boxes) == 0:
            return entities[name]
        s = sorted(boxes, key=lambda x: boxDist(theBox, x))
        print name, "stuff:", (map (lambda x: boxDist(theBox, x), s))
        dist = boxDist(theBox, s[0])
        if dist < entities[name].dist:
            return Entity(theBox, s[0], dist)

    for oBox in getBoxes(pos['blue']):
        blueT_Body = getClosest(oBox, 'objects')

    for oBox in getBoxes(pos['ball']):
        ball = getClosest(oBox, 'objects')
        yellowAndBall = getClosest(oBox, 'yellow')

    for oBox in getBoxes(pos['yellow']):
        yellowT_Body = getClosest(oBox, 'objects')

    for oBox in getBoxes(pos['dirmarker']):
        yellowT_Body = getClosest(oBox, 'objects')

    # TODO: is == defined as expected?
    if yellowT_Body == yellowAndBall:
        print "The yellow T appears to be the same as the ball mask D:"

    # What if?
    # - blue/yellow lack dirmarkers?
    #if not pos['yellow'] or
    # - yellow is missing?
    # - blue is missing?
    # - ball is missing?

    entities['blue']   = blueT_Body
    entities['yellow'] = yellowT_Body
    entities['ball']   = ball


    # for oBox in getBoxes
    #
    #         entities[name] =
    # for oBox in getBoxes(pos['objects']):
    #     entities['ball'] = getClosest(, 'yellow')

    print "Balls found:", len(pos['ball'])

    return entities

    # entities['ball'] = [ x
    #                      for x in pos['ball']
    #                      for y in pos['ball']
    #                      if boxDist(x, y) < BALL_MAX_DIST ]

def boxDist(A, B):
    x1, y1 =  BoxCenterPos(A)
    x2, y2 =  BoxCenterPos(B)
    return math.sqrt( (x2 - x1)**2 + (y2 - y1)**2 )

def getCenters():
    """
    [ (CvBox2D, CvRect) ] ) -> dict( label -> (CvBox2D, CvRect) )
    """
    pass
