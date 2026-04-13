import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__),'..'))
from game import Board
import pygame
import numpy as np

class draw:
    def __init__(self,width,height,screen):
        self.width=int(0.307*width)
        self.height=self.width
        self.color=(10,10,10)
        self.screen=screen
        self.padding=self.width*0.01
        self.cell_size=(self.width-self.padding*15)/10
        self.radius=int(self.cell_size*0.1)
        self.color1=(0, 229, 255)
        self.color2=(224, 64, 251)
        self.grid=pygame.Rect((width-self.width)/2+0.007*self.width,(height-self.height)/2+0.006*self.width,self.width,self.height)
    def draw_board(self,info):
        pygame.draw.rect(self.screen,self.color,self.grid,border_radius=10)
        mx, my = pygame.mouse.get_pos()
        w,h=self.screen.get_size()
        pygame.draw.rect(self.screen,self.color1,
                        pygame.Rect(0.058*w,0.185*h,0.0745*h,0.0745*h),border_radius=5,width=3)
        pygame.draw.rect(self.screen,self.color2,
                         pygame.Rect(0.91*w,0.185*h,0.0745*h,0.0745*h),border_radius=5,width=3)
        self.draw_x(self.screen,pygame.Rect(0.058*w,0.185*h,0.0745*h,0.0745*h),self.color1)
        self.draw_o(self.screen,pygame.Rect(0.91*w,0.185*h,0.0745*h,0.0745*h),self.color2)
        for i in range(10):
            for j in range(10):

                x = self.padding*3 + j * (self.cell_size + self.padding) + self.grid.x
                y = self.padding*3 + i * (self.cell_size + self.padding) +self.grid.y

                rect = pygame.Rect(x, y, self.cell_size, self.cell_size)

                # Hover effect
                if rect.collidepoint(mx, my):
                    color = (70,70,70)
                else:
                    color = (50,50,50)

                pygame.draw.rect(
                    self.screen,
                    color,
                    rect,
                    border_radius=self.radius
                )
                if info[i][j]==1:
                    self.draw_x(self.screen,rect,self.color1)
                elif info[i][j]==2:
                    self.draw_o(self.screen,rect,self.color2)
    def draw_x(self,surface, rect,color):
        x,y,size,_=rect
        half = size // 2
        x+=half
        y+=half
        half=half//2
        pygame.draw.line(surface, color, (x - half, y - half), (x + half, y + half), max(int(8/60*size),1))
        pygame.draw.line(surface, color, (x + half, y - half), (x - half, y + half), max(int(8/60*size),1))
        pygame.draw.line(surface, (240, 240, 255), (x - half, y - half), (x + half, y + half), max(int(2/60*size),1))
        pygame.draw.line(surface, (240, 240, 255), (x + half, y - half), (x - half, y + half), max(int(2/60*size),1))
    def draw_o(self,surface, rect,color):
        x,y,radius,_=rect
        radius=radius//2
        x+=radius
        y+=radius
        radius=int(radius*0.6)
        pygame.draw.circle(surface, color, (x, y), radius, max(1,int(6/18*radius)))
        pygame.draw.circle(surface, (240,240,255), (x, y), radius, max(int(2/18*radius),1))

class Tictactoe(Board):
    def __init__(self,width,height,screen):
        self.playing_board=draw(width,height,screen)
        self.board=np.zeros((10,10))
        self.screen=screen
        self.turn=1
    def maximize(self,width,height,screen):
        self.playing_board=draw(width,height,screen)
        self.playing_board.draw_board(self.board)
        self.screen=screen
    def reset(self):
        self.board=np.zeros((10,10))
    def play(self, turn, event=None):
        self.playing_board.draw_board(self.board)  # always redraw full board

        if event and event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            row, col = -1, -1
            for i in range(10):
                for j in range(10):
                    x = self.playing_board.padding*3 + j * (self.playing_board.cell_size + self.playing_board.padding) + self.playing_board.grid.x
                    y = self.playing_board.padding*3 + i * (self.playing_board.cell_size + self.playing_board.padding) + self.playing_board.grid.y
                    rect = pygame.Rect(x, y, self.playing_board.cell_size, self.playing_board.cell_size)
                    if rect.collidepoint(mx, my):
                        row, col = i, j
                        break

            if row != -1 and self.board[row][col] == 0:
                self.board[row][col] = turn  # update board STATE
                return True
        return False
    def win_check(self,turn):
        if self.check_hori_vert(turn):
            return turn
        if self.check_diagonal(turn):
            return turn
        if self.check_draw():
            return 0
        return "none"
    def check_hori_vert(self,turn):
        mask = (self.board == turn).astype(int)

        # Horizontal: stack shifted versions and sum across axis
        h = mask[:, 0:6] + mask[:, 1:7] + mask[:, 2:8] + mask[:, 3:9] + mask[:, 4:10]
        
        # Vertical: same but along rows
        v = mask[0:6, :] + mask[1:7, :] + mask[2:8, :] + mask[3:9, :] + mask[4:10, :]

        return bool((h >= 5).any() or (v >= 5).any())
    def check_diagonal(self,turn):
        mask = (self.board == turn).astype(int)

        # Main diagonal (top-left to bottom-right): shift down+right
        d1 = (mask[0:6, 0:6] + mask[1:7, 1:7] + mask[2:8, 2:8] + 
            mask[3:9, 3:9] + mask[4:10, 4:10])

        # Anti diagonal (top-right to bottom-left): shift down+left
        d2 = (mask[0:6, 4:10] + mask[1:7, 3:9] + mask[2:8, 2:8] + 
            mask[3:9, 1:7] + mask[4:10, 0:6])

        return bool((d1 >= 5).any() or (d2 >= 5).any())
    def check_draw(self):
        return bool((self.board != 0).all())
    def turn_change(self,changed):
        if changed:
            if self.turn==1:
                self.turn=2
            else:
                self.turn=1



