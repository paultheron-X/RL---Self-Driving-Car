import pygame
from torch import argmin
from game_utils.constants import *
from game_utils.geometry import *
import numpy as np

# The Rays going in all the directions from the car

class Vision():
    def __init__(self, x, y, vec) -> None:
        self.x = x
        self.y = y
        self.orig = Point(x,y)
        self.vec = vec 
        self.inf = self.coord_inf()             

    def coord_inf(self):     # Returns infinite point coords, parametric equation
        t=10000
        x_inf = self.x + t * self.vec.x
        y_inf = self.y + t * self.vec.y 
        return Point(x_inf, y_inf)

    def one_intersects(self, wall):    # returns true, iif ray intersects the wall
        return intersect(self.orig, self.inf, wall.get_start(), wall.get_last())
    
    def track_intersection(self, walls):
        distances = [np.inf for a in range(len(walls))]
        points = [Point(0,0) for a in distances]

        for i,wall in enumerate(walls):
            if self.one_intersects(wall):
                points[i] = intersect_point_fixed([self.orig, self.inf], [wall.get_start(), wall.get_last()])
                distances[i] = self.orig.dist(points[i])
        indmin = np.argmin(distances)
        return (points[indmin], distances[indmin])

    def dray_ray(self, endpoint, screen):
        if not (endpoint == Point(0,0)):
            pygame.draw.aaline(screen, GREEN , start_pos=self.orig, end_pos=endpoint, blend = 5)
            #pygame.draw.circle(screen, BLUE, self.orig, 1, width = 2)
            pygame.draw.circle(screen, BLUE, endpoint, 2)