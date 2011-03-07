from math import *
import numpy as np
from common.world import World

def dist(a,b):
    return sqrt( (a[0]-b[0])**2 + (a[1]-b[1])**2 )

def attractive_field(target, pos, scale, max_dist):
    dx,dy = target[0]-pos[0], target[1]-pos[1]
    angle = atan2(dy,dx)
    _dist = min(max_dist, dist(target, pos))
    Fx = scale[0]*_dist*cos(angle)
    Fy = scale[1]*_dist*sin(angle)
    return np.array((Fx,Fy))

def repulsive_field(target, pos, scale, max_dist, offset=[0,0]):
    dx,dy = target[0]-pos[0], target[1]-pos[1]
    angle = atan2(dy,dx)
    _dist = min(max_dist, dist(target, pos))
    Fx = -scale[0]*(max_dist - _dist)*cos(angle + offset[0])
    Fy = -scale[1]*(max_dist - _dist)*sin(angle + offset[1])
    return np.array((Fx,Fy))

def tangential_field(direction, *args):
    return repulsive_field(*args, offset=[direction*pi/2]*2)

def repulsive_field_vertical(Y, pos, scale, max_dist):
    dist = max(0, max_dist - abs(pos[1] - Y)) #**2
    return np.array((0, -scale*dist))

def repulsive_field_horizontal(X, pos, scale, max_dist):
    dist = max(0, max_dist - abs(pos[0] - X))
    return np.array((-scale*dist, 0))

def all_apf(pos, end, *args):
    return ball_apf(pos, *args) \
        + wall_apf(pos, end) \
        + random_apf()

def opponent_apf(target, pos):
    scale = [1,1]
    max_dist = 80
    print target, pos
    return repulsive_field(target, pos, scale, max_dist)

def random_apf(scale=0.2):
    return (scale*np.random.random(), scale*np.random.random())

def wall_apf(pos, (X,Y), offset=0, scale=1):
    max_dist = 75
    scale *= 0.3
    top = repulsive_field_vertical(0, pos, -scale, max_dist)
    bottom = repulsive_field_vertical(Y, pos, scale, max_dist)

    left = repulsive_field_horizontal(0, pos, -scale, max_dist)
    right = repulsive_field_horizontal(X, pos, scale, max_dist)

    return top+bottom+left+right

scaleT1 = 0.5
scaleT2 = 0.5
scaleA = 0.01
offset = -0.5

def ball_apf(pos, ball_pos, goal_pos, radius):
    S=3; max_dist = S*50

    # Eliminate outliers
    if dist(pos, ball_pos) < S*radius: return [0,0]

    Gx,Gy = goal_pos[0]-ball_pos[0], goal_pos[1]-ball_pos[1]
    angle = atan2(Gy,Gx)
    angleN = pi/2 + angle

    G1x = ball_pos[0] + S*scaleT1*(cos(angleN) + offset*sin(angle))
    G1y = ball_pos[1] + S*scaleT1*(sin(angleN) + offset*cos(angle))
    G1 = G1x, G1y
    tangent1 = tangential_field(1, G1, pos, [S*scaleT2]*2, max_dist)

    G2x = ball_pos[0] + S*scaleT1*(cos(pi+angleN) - offset*sin(angle))
    G2y = ball_pos[1] + S*scaleT1*(sin(pi+angleN) - offset*cos(angle))
    G2 = G2x, G2y
    tangent2 = tangential_field(-1, G2, pos, [S*scaleT2]*2, max_dist)

    attractive = attractive_field(ball_pos, pos, [S*scaleA]*2, max_dist)

    return tangent1+tangent2+attractive

    # vecs = tangent1,tangent2,attractive
    # mags = map(mag, vecs)
    # angles = sum(map(lambda (x,y):(y,x), vecs))
    # angle = atan2(*angles)
    # for mag,angle in zip(mags, angles):
    #     res.append( np.array([mag*cos(angle), mag*sin(angle)]) )
    # return sum(res)
