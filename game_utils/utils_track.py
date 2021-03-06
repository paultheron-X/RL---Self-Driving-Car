from cgitb import grey
import pygame
from pygame.locals import *
from game_utils.constants import *
from game_utils.geometry import *
import pandas as pd
from numpy import genfromtxt

class Wall:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def draw_wall(self, screen, linewidth=2, color = GREY):
        pygame.draw.line(screen, color , start_pos=(self.x1, self.y1), end_pos=(self.x2, self.y2), width=linewidth)
    
    def get_start(self):
        return Point((self.x1), (self.y1))
    
    def get_last(self):
        return Point((self.x2), (self.y2))

class Portal(Wall):
    def __init__(self, x1, y1, x2, y2, active = False):
        super().__init__(x1, y1, x2, y2)
        self.is_active = active
    
    def set_active(self):
         self.is_active = True
    
    def set_inactive(self):
         self.is_active = False
    
    def draw_portal(self, screen):
        if self.is_active:
            self.draw_wall(screen, color= RED)
        else:
            self.draw_wall(screen, color = BLUE)


class Track:
    def __init__(self, screen, off = OFFSET):
        self.list_walls = []
        self.poly_ext = []
        self.poly_int = []
        self.list_portals = []

        height = screen.get_height()
        width = screen.get_width()

        self.screen = screen

        offset_x = off * width
        offset_y = off * height
        vx = (1-2*off) * width / 10
        vy = (1-2*off) * height / 10
        

        # Wall creation, see paper - picture for details
        if EASY_MAP:
        # External
            wall00 = Wall(offset_x + 1 * vx, offset_y, offset_x + 6 * vx, offset_y)
            wall10 = Wall(offset_x + 6 * vx, offset_y, offset_x + 8 * vx,  offset_y )
            wall20 = Wall(offset_x + 8 * vx,  offset_y , offset_x + 9 * vx, offset_y + 1 * vy)
            wall30 = Wall(offset_x + 9 * vx, offset_y + 1 * vy, offset_x + 10 * vx, offset_y + 2 * vy )
            wall40 = Wall(offset_x + 10 * vx, offset_y + 2 * vy, offset_x + 10 * vx, offset_y + 4 * vy )
            wall50 = Wall(offset_x + 10 * vx, offset_y + 4 * vy, offset_x + 10 * vx, offset_y + 7 * vy)
            wall60 = Wall(offset_x + 10 * vx, offset_y + 7 * vy, offset_x + 9 * vx, offset_y + 9 * vy)
            wall70 = Wall(offset_x + 9 * vx, offset_y + 9 * vy, offset_x + 7 * vx, offset_y + 10 * vy)
            wall80 = Wall(offset_x + 7 * vx, offset_y + 10 * vy, offset_x + 3 * vx, offset_y + 10 * vy)
            wall90 = Wall(offset_x + 3 * vx, offset_y + 10 * vy, offset_x + 1 * vx, offset_y + 9 * vy)
            wall100 = Wall(offset_x + 1 * vx, offset_y + 9 * vy, offset_x, offset_y + 7 * vy)
            wall110 = Wall(offset_x, offset_y + 7 * vy, offset_x, offset_y + 1 * vy)
            wall120 = Wall(offset_x, offset_y + 1 * vy, offset_x + 0.25 * vx, offset_y + 0.25 * vy)
            wall130 = Wall(offset_x + 0.25 * vx, offset_y + 0.25 * vy, offset_x + 1 * vx, offset_y)
            

            # Internal

            off = DECAL*off
            offset_x = off * width
            offset_y = off * height
            vx = (1-2*off) * width / 10
            vy = (1-2*off) * height / 10

            wall01 = Wall(offset_x + 1 * vx, offset_y, offset_x + 6 * vx, offset_y)
            wall11 = Wall(offset_x + 6 * vx, offset_y, offset_x + 8 * vx,  offset_y )
            wall21 = Wall(offset_x + 8 * vx,  offset_y , offset_x + 9 * vx, offset_y + 1 * vy)
            wall31 = Wall(offset_x + 9 * vx, offset_y + 1 * vy, offset_x + 10 * vx, offset_y + 2 * vy )
            wall41 = Wall(offset_x + 10 * vx, offset_y + 2 * vy, offset_x + 10 * vx, offset_y + 4 * vy )
            wall51 = Wall(offset_x + 10 * vx, offset_y + 4 * vy, offset_x + 10 * vx, offset_y + 7 * vy)
            wall61 = Wall(offset_x + 10 * vx, offset_y + 7 * vy, offset_x + 9 * vx, offset_y + 9 * vy)
            wall71 = Wall(offset_x + 9 * vx, offset_y + 9 * vy, offset_x + 7 * vx, offset_y + 10 * vy)
            wall81 = Wall(offset_x + 7 * vx, offset_y + 10 * vy, offset_x + 3 * vx, offset_y + 10 * vy)
            wall91 = Wall(offset_x + 3 * vx, offset_y + 10 * vy, offset_x + 1 * vx, offset_y + 9 * vy)
            wall101 = Wall(offset_x + 1 * vx, offset_y + 9 * vy, offset_x, offset_y + 7 * vy)
            wall111 = Wall(offset_x, offset_y + 7 * vy, offset_x, offset_y + 1 * vy)
            wall121 = Wall(offset_x, offset_y + 1 * vy, offset_x + 0.25 * vx, offset_y + 0.25 * vy)
            wall131 = Wall(offset_x + 0.25 * vx, offset_y + 0.25 * vy, offset_x + 1 * vx, offset_y)

            '''  # Old Track
            wall01 = Wall(offset_x + 1 * vx, offset_y, offset_x + 6 * vx, offset_y)
            wall11 = Wall(offset_x + 6 * vx, offset_y, offset_x + 6.5 * vx,  offset_y + 1 * vy)
            wall21 = Wall(offset_x + 6.5 * vx,  offset_y + 1 * vy, offset_x + 8.5 * vx, offset_y + 1 * vy)
            wall31 = Wall(offset_x + 8.5 * vx, offset_y + 1 * vy, offset_x + 10 * vx, offset_y + 4 * vy )
            wall41 = Wall(offset_x + 8.5 * vx, offset_y + 1 * vy, offset_x + 10 * vx, offset_y + 4 * vy )
            wall51 = Wall(offset_x + 10 * vx, offset_y + 4 * vy, offset_x + 10 * vx, offset_y + 7 * vy)
            wall61 = Wall(offset_x + 10 * vx, offset_y + 7 * vy, offset_x + 9 * vx, offset_y + 9 * vy)
            wall71 = Wall(offset_x + 9 * vx, offset_y + 9 * vy, offset_x + 7 * vx, offset_y + 10 * vy)
            wall81 = Wall(offset_x + 7 * vx, offset_y + 10 * vy, offset_x + 3 * vx, offset_y + 10 * vy)
            wall91 = Wall(offset_x + 3 * vx, offset_y + 10 * vy, offset_x + 1 * vx, offset_y + 9 * vy)
            wall101 = Wall(offset_x + 1 * vx, offset_y + 9 * vy, offset_x, offset_y + 7 * vy)
            wall111 = Wall(offset_x, offset_y + 7 * vy, offset_x, offset_y + 1 * vy)
            wall121 = Wall(offset_x, offset_y + 1 * vy, offset_x + 0.25 * vx, offset_y + 0.25 * vy)
            wall131 = Wall(offset_x + 0.25 * vx, offset_y + 0.25 * vy, offset_x + 1 * vx, offset_y)
            '''
            

            #wall00 = Wall(0, 50, 10,0)
            for i in range(NUM_WALLS):
                self.list_walls.append(eval('wall' + str(i)+str(0)))
                self.list_walls.append(eval('wall' + str(i)+str(1)))
                pt1 = eval('wall' + str(i)+str(0)).get_start()
                pt2 = eval('wall' + str(i)+str(1)).get_start()
                self.poly_ext.append(pt1)
                self.poly_int.append(pt2)
        
        else:
            pts_array = genfromtxt("map/map2/sample.csv", delimiter=",")
            for i, a in enumerate(pts_array):
                coeff = height/720
                first_pt_ext =  (offset_x + 0.85*pts_array[i][0],offset_y +  0.85*(height- coeff*pts_array[i][1]))
                next_pt_ext =  (offset_x + 0.85*pts_array[(i+1) % NUM_WALLS][0],offset_y + 0.85*(height- coeff*pts_array[(i+1) % NUM_WALLS][1]))
                first_pt_int =  (offset_x + 0.85*pts_array[i][2],offset_y + 0.85*(height- coeff*pts_array[i][3]))
                next_pt_int =  (offset_x + 0.85*pts_array[(i+1) % NUM_WALLS][2],offset_y + 0.85*(height-  coeff*pts_array[(i+1) % NUM_WALLS][3]))
                
                wext = Wall(first_pt_ext[0], first_pt_ext[1], next_pt_ext[0], next_pt_ext[1])
                wint = Wall(first_pt_int[0], first_pt_int[1], next_pt_int[0], next_pt_int[1])
                
                self.list_walls.append(wext)
                self.list_walls.append(wint)
                pt1 = wext.get_start()
                pt2 = wint.get_start()
                self.poly_ext.append(pt1)
                self.poly_int.append(pt2)
                
        
        points_supportext = []
        points_supportint = []
        for i, a in enumerate(self.poly_ext):
            if i==0:
                points_supportext += subdivise(a, self.poly_ext[ (i+1) % NUM_WALLS ] , 3, force=True)
                points_supportint += subdivise(self.poly_int[i], self.poly_int[ (i+1) % NUM_WALLS ] , 3, force=True)
            else:
                points_supportext += subdivise(a, self.poly_ext[ (i+1) % NUM_WALLS ] , 3)
                points_supportint += subdivise(self.poly_int[i], self.poly_int[ (i+1) % NUM_WALLS ] , 3)
                
        for i,a in enumerate(points_supportext):
            pt1 = a
            pt2 = points_supportint[i]
            self.list_portals.append(Portal(pt1.x, pt1.y, pt2.x, pt2.y))

    def draw_track(self):
        for wall in self.list_walls:
            wall.draw_wall(self.screen)
        pygame.draw.polygon(self.screen, GREY_LIGHT, self.poly_ext)
        pygame.draw.polygon(self.screen, BLACK, self.poly_int)

    def get_walls(self):
        return self.list_walls.copy()
    
    def get_portals(self):
        return self.list_portals.copy()  
