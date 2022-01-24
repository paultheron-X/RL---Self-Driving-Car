import pygame 
import math
import numpy as np
from constants import *
from numpy.linalg import inv


class Point(pygame.math.Vector2):
    def __init__(self, x, y) -> None:
        super().__init__()
        self.x = x
        self.y = y 
    
    def to_tuple(self):
        return (self.x, self.y)
    
    def dist(self, P):
        return np.sqrt((self.x - P.x)**2 + (self.y - P.y)**2)


# Code to check if segment AB and CD intersect

def ccw(A,B,C):
    return (C.y-A.y) * (B.x-A.x) > (B.y-A.y) * (C.x-A.x)

def intersect(A,B,C,D):  # returns True if there is an intersection
    return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)

def intersect_point_fixed(line1, line2):
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
       raise Exception('lines do not intersect')

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return Point(x, y)


#-----
# Code for rotations --> angle in radians

def rotate_point_around_center(center,point,angle_):
    angle = math.radians(angle_)
    qx = center.x + math.cos(angle) * (point.x - center.x) + math.sin(angle) * (point.y - center.y)
    qy = center.y + math.sin(angle) * (point.x - center.x) - math.cos(angle) * (point.y - center.y)
    q = Point(qx, qy)
    return q

def rotate_rect(pt1, pt2, pt3, pt4, angle):

    pt_center = Point((pt1.x + pt3.x)/2, (pt1.y + pt3.y)/2)

    '''pt1 = rotate_point_around_center(pt_center,pt1,angle)
    pt2 = rotate_point_around_center(pt_center,pt2,angle)
    pt3 = rotate_point_around_center(pt_center,pt3,angle)
    pt4 = rotate_point_around_center(pt_center,pt4,angle)'''
    
    pt1 = pt1.rotate(angle)
    pt2 = pt2.rotate(angle)
    pt3 = pt3.rotate(angle)
    pt4 = pt4.rotate(angle)

    return pt1, pt2, pt3, pt4