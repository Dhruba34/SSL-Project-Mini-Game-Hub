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
                



'''import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 700, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rounded Grid")

BG = (20, 20, 20)
TILE_COLOR = (40, 40, 40)
HOVER_COLOR = (70, 70, 70)

ROWS, COLS = 10, 10
PADDING = 6   # space between tiles
RADIUS = 10   # corner roundness

cell_size = (WIDTH - (COLS + 1) * PADDING) // COLS

def draw_grid():
    mx, my = pygame.mouse.get_pos()

    for i in range(ROWS):
        for j in range(COLS):

            x = PADDING + j * (cell_size + PADDING)
            y = PADDING + i * (cell_size + PADDING)

            rect = pygame.Rect(x, y, cell_size, cell_size)

            # Hover effect
            if rect.collidepoint(mx, my):
                color = HOVER_COLOR
            else:
                color = TILE_COLOR

            pygame.draw.rect(
                screen,
                color,
                rect,
                border_radius=RADIUS
            )

while True:
    screen.fill(BG)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    draw_grid()
    pygame.display.update()'''