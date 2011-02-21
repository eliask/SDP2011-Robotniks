from math import *

def dist(a,b):
    return sqrt( (a[0]-b[0])**2 + (a[1]-b[1])**2 )

def attractive_field(target, pos, scale, max_dist):
    dx,dy = target[0]-pos[0], target[1]-pos[1]
    angle = atan2(dy,dx)
    _dist = min(max_dist, dist(target, pos))
    Fx = scale*_dist*cos(angle)
    Fy = scale*_dist*sin(angle)
    return Fx,Fy

def repulsive_field(target, pos, scale, max_dist, offset=[0,0]):
    dx,dy = target[0]-pos[0], target[1]-pos[1]
    angle = atan2(dy,dx)
    _dist = min(max_dist, dist(target, pos))
    Fx = -scale*(max_dist - _dist)*cos(angle + offset[0])
    Fy = -scale*(max_dist - _dist)*sin(angle + offset[1])
    return Fx,Fy

def tangential_field(direction, *args):
    return repulsive_field(*args, offset=[direction*pi/2]*2)

def ball_apf(pos, ball_pos, goal_pos, scale, max_dist, radius):
    # Eliminate outliers
    if dist(pos, ball_pos) < radius: return [0,0]

    Gx,Gy = goal_pos[0]-ball_pos[0], goal_pos[1]-ball_pos[1]
    angleN = pi/2 + atan2(Gy,Gx)

    G1x = ball_pos[0] + scale*cos(angleN)
    G1y = ball_pos[1] + scale*sin(angleN)
    G1 = G1x, G1y
    tangent1 = tangential_field(1, G1, pos, scale, max_dist)

    G2x = ball_pos[0] + scale*cos(pi+angleN)
    G2y = ball_pos[1] + scale*sin(pi+angleN)
    G2 = G2x, G2y
    tangent2 = tangential_field(-1, G2, pos, scale, max_dist)

    return tangent1[0]+tangent2[0], tangent1[1]+tangent2[1]

