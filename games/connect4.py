import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__),'..'))
from game import Board
import pygame
import numpy as np

class draw:
    def __init__(self,width,height,screen):
        self.width=int(min(width*0.8,height*0.8))
        self.height=int(min(height*0.8,width*0.8))
        self.color=(10,10,10)
        self.screen=screen
        self.padding=int(self.width*0.01)
        self.cell_width=int((self.width-self.padding*12)//7)
        self.cell_height=int(self.height-self.padding*6)
        self.radius=int(self.cell_width*0.1)
        self.grid=pygame.Rect((width-self.width)//2,(height-self.height)//2,self.width,self.height)
    def draw_board(self,info):
        pygame.draw.rect(self.screen,self.color,self.grid,border_radius=10)
        mx, my = pygame.mouse.get_pos()

        for i in range(7):

            x = self.padding*3 + i * (self.cell_width + self.padding) + self.grid.x
            y = self.padding*3 + self.grid.y

            rect = pygame.Rect(x, y, self.cell_width, self.cell_height)

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
            for j in range(7):
                recti=pygame.Rect(x,y+j*(self.padding+self.cell_width),self.cell_width,self.cell_width)
                if info[j][i]==1:
                    self.draw_piece(self.screen,recti,(250,140,106))
                elif info[j][i]==2:
                    self.draw_piece(self.screen,recti,(87,200,217))
    def draw_piece(self,surface, rect, color):
        center = rect.center
        radius = int(rect.width*0.25)

        pygame.draw.circle(surface, color, center, radius,0)


class Connect4(Board):
    def __init__(self,width,height,screen):
        self.playing_board=draw(width,height,screen)
        self.board=np.zeros((7,7))
        self.screen=screen
        self.turn=1
    def maximize(self,width,height,screen):
        self.playing_board=draw(width,height,screen)
        self.playing_board.draw_board(self.board)
        self.screen=screen
    def reset(self):
        self.board=np.zeros((7,7))
    def play(self, turn, event=None):
        self.playing_board.draw_board(self.board)  # always redraw full board

        if event and event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            col=-1
            for i in range(7):
                x = self.playing_board.padding*3 + i * (self.playing_board.cell_width + self.playing_board.padding) + self.playing_board.grid.x
                y = self.playing_board.padding*3 + self.playing_board.grid.y
                rect = pygame.Rect(x, y, self.playing_board.cell_width, self.playing_board.cell_height)
                if rect.collidepoint(mx, my):
                    col=i
                    break

            if col != -1:
                row=-1
                for i in range(6,-1,-1):
                    if self.board[i][col]==0:
                        row=i
                        break
                if row!=-1:
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
        h = mask[:, 0:4] + mask[:, 1:5] + mask[:, 2:6] + mask[:, 3:7]
        
        # Vertical: same but along rows
        v = mask[0:4, :] + mask[1:5, :] + mask[2:6, :] + mask[3:7, :]

        return bool((h >= 4).any() or (v >= 4).any())
    def check_diagonal(self,turn):
        mask = (self.board == turn).astype(int)

        # Main diagonal (top-left to bottom-right): shift down+right
        d1 = mask[0:4, 0:4] + mask[1:5, 1:5] + mask[2:6, 2:6] + mask[3:7, 3:7]

        # Anti diagonal (top-right to bottom-left): shift down+left
        d2 = mask[0:4, 3:7] + mask[1:5, 2:6] + mask[2:6, 1:5] + mask[3:7, 0:4]

        return bool((d1 >= 4).any() or (d2 >= 4).any())
    def check_draw(self):
        return bool((self.board != 0).all())
    def turn_change(self,changed):
        if changed:
            if self.turn==1:
                self.turn=2
            else:
                self.turn=1



