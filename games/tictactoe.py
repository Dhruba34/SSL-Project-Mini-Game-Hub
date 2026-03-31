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
        self.cell_size=int((self.width-self.padding*15)//10)
        self.radius=int(self.cell_size*0.1)
        self.grid=pygame.Rect((width-self.width)//2,(height-self.height)//2,self.width,self.height)
    def draw_board(self,info):
        pygame.draw.rect(self.screen,self.color,self.grid,border_radius=10)
        mx, my = pygame.mouse.get_pos()

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
                    self.draw_x(self.screen,rect,(255,255,255))
                elif info[i][j]==2:
                    self.draw_o(self.screen,rect,(255,255,255))
    def draw_x(self,surface, rect, color):
        padding = rect.width // 4

        pygame.draw.line(
            surface,
            color,
            (rect.left + padding, rect.top + padding),
            (rect.right - padding, rect.bottom - padding),
            5,
        )
        pygame.draw.line(
            surface,
            color,
            (rect.right - padding, rect.top + padding),
            (rect.left + padding, rect.bottom - padding),
            5,
        )
    def draw_o(self,surface, rect, color):
        center = rect.center
        radius = rect.width // 2 - rect.width // 4

        pygame.draw.circle(surface, color, center, radius, 5)


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



