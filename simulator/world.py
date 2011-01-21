from pygame.locals import *

class World:

    image_names = {
        'bg'     : 'vision/media/calibrated-background-cropped.png',
        'blue'   : 'simulator/blue_robot.png',
        'yellow' : 'simulator/yellow_robot.png',
        'ball'   : 'simulator/ball.png',
        }

    Resolution = (768, 424)

    Pitch = Rect(6, 28, 754, 378)
    # This looks reasonable enough, but if the goal was centered exactly,
    # it would start from y~=126 and end at y~=308 (assuming the same size)
    LeftGoalArea= Rect(0, 132, 6, 181)
    RightGoalArea= Rect(760, 132, 9, 181)

    LeftStartPos  = ( LeftGoalArea.left + 130,
                      LeftGoalArea.top +  LeftGoalArea.height/2 )
    RightStartPos = ( RightGoalArea.right - 130,
                      RightGoalArea.top + RightGoalArea.height/2 )

    def __init__(self):
        self.ents = {}
