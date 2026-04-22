import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__),'..'))
from game import Board
import pygame
import numpy as np
import time
import math

class draw:
    def __init__(self, width, height, screen):
        self.screen = screen
        self.width = width
        self.height = height
        self.start_center=(int(0.333866*width),int(0.225876*height))
        self.hori_centers=int(0.055995*width)
        self.height_centers=int(0.107*height)
        self.radius=min(int(0.014285*width),int(0.054173*height))
        self.piece1=pygame.transform.scale(pygame.image.load("./pictures/blue.png"),(2*self.radius,2*self.radius))
        self.piece2=pygame.transform.scale(pygame.image.load("./pictures/black.png"),(2*self.radius,2*self.radius))
        self.icon1=pygame.transform.scale(pygame.image.load("./pictures/icon1.png"),(int(0.08864*width),int(0.1739*height)))
        self.icon2=pygame.transform.scale(pygame.image.load("./pictures/icon2.png"),(int(0.08864*width),int(0.1739*height)))
        self.plate=pygame.transform.scale(pygame.image.load("./pictures/plate.png"),(int(0.1143*width),int(0.0565*height)))
        self.player1=pygame.transform.scale(pygame.image.load("./pictures/player1.png"),(int(0.1165*width),int(0.0522*height)))
        self.player2=pygame.transform.scale(pygame.image.load("./pictures/player2.png"),(int(0.1165*width,),int(0.0522*height)))
    def draw_board(self,info):
        for i in range(7):
            for j in range(7):
                center=(j*self.hori_centers+self.start_center[0],i*self.height_centers+self.start_center[1])
                if info[i][j]==1:
                    self.draw_piece(self.screen,center,self.piece1)
                elif info[i][j]==2:
                    self.draw_piece(self.screen,center,self.piece2)
        self.screen.blit(self.icon1,(int(0.0747*self.width),int(0.1957*self.height)))
        self.screen.blit(self.icon2,(int(0.83956*self.width),int(0.1957*self.height)))
        self.screen.blit(self.plate,(int(0.0593*self.width),int(0.3739*self.height)))
        self.screen.blit(self.plate,(int(0.832967*self.width),int(0.3739*self.height)))
        self.screen.blit(self.player1,(int(0.06*self.width),int(0.1203*self.height)))
        self.screen.blit(self.player2,(int(0.8264*self.width),int(0.1203*self.height)))

    def draw_piece(self, surface,center,piece):
        surface.blit(piece,(center[0]-self.radius,center[1]-self.radius))

class Connect4(Board):
    def __init__(self,width,height,screen):
        self.playing_board=draw(width,height,screen)
        self.board=np.zeros((7,7))
        self.screen=screen
        self.turn=1
        self.animate=False
        self.prev_animate=False
        self.winner=0
        self.highlight_time=0.3
    def maximize(self,width,height,screen):
        self.playing_board=draw(width,height,screen)
        self.playing_board.draw_board(self.board)
        self.screen=screen
    def reset(self):
        self.board=np.zeros((7,7))
    def play(self, turn, event=None):
        self.playing_board.draw_board(self.board)

        if event and event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            col = -1
            for i in range(7):
               x=self.playing_board.start_center[0]-self.playing_board.hori_centers//2+i*self.playing_board.hori_centers
               y=self.playing_board.start_center[1]-self.playing_board.height_centers//2
               rect=pygame.Rect(x,y,self.playing_board.hori_centers,self.playing_board.height_centers*7)
               if rect.collidepoint(mx, my):
                    col = i
                    break

            if col != -1:
                row = -1
                for i in range(6, -1, -1):
                    if self.board[i][col] == 0:
                        row = i
                        break
                if row != -1:
                    self.board[row][col] = turn
                    return True
        return False
    def win_check(self,turn):
        if self.animate==False and self.prev_animate==False:
            if self.check_hori_vert(turn):
                self.playing_board.draw_board(self.board)
                self.winner=turn
            if self.check_diagonal(turn):
                self.playing_board.draw_board(self.board)
                self.winner=turn
            if self.check_draw():
                self.playing_board.draw_board(self.board)
                return 0
        elif self.animate==True:
            self.highlight()
            self.prev_animate=True
        elif self.animate==False and self.prev_animate==True:
            return self.winner
        return "none"
    def check_hori_vert(self,turn):
        mask = (self.board == turn).astype(int)

        # Horizontal: stack shifted versions and sum across axis
        h = mask[:, 0:4] + mask[:, 1:5] + mask[:, 2:6] + mask[:,3:7]
        
        # Vertical: same but along rows
        v = mask[0:4, :] + mask[1:5, :] + mask[2:6, :] + mask[3:7, :]

        if bool((h >= 4).any()):
            row,col=np.where(h==4)
            row=row[0]
            col=col[0]
            self.match=np.stack((np.ones(4)*row,np.arange(col,col+4)),axis=1)
            self.animate=True
            return True
        elif bool((v>=4).any()):
            row,col=np.where(v==4)
            row=row[0]
            col=col[0]
            self.match=np.stack((np.arange(row,row+4),np.ones(4)*col),axis=1)
            self.animate=True
            return True
        return False        
        
    def check_diagonal(self,turn):
        mask = (self.board == turn).astype(int)

        # Main diagonal (top-left to bottom-right): shift down+right
        d1 = (mask[0:4, 0:4] + mask[1:5, 1:5] + mask[2:6, 2:6] + mask[3:7, 3:7])

        # Anti diagonal (top-right to bottom-left): shift down+left
        d2 = (mask[0:4, 3:7] + mask[1:5, 2:6] + mask[2:6, 1:5] + mask[3:7, 0:4])

        if bool((d1 >= 4).any()):
            row,col=np.where(d1==4)
            row=row[0]
            col=col[0]
            self.match=np.stack((np.arange(row,row+4),np.arange(col,col+4)),axis=1)
            self.animate=True
            return True
        elif bool((d2>=5).any()):
            row,col=np.where(d2==4)
            row=row[0]
            col=col[0]+4
            self.match=np.stack((np.arange(row,row+4),np.arange(col,col-4,-1)),axis=1)
            self.animate=True
            return True
        return False
    def check_draw(self):
        return bool((self.board != 0).all())
    def highlight(self):
        if not self.prev_animate:
            self.t0=time.time()
        elapsed=float(time.time()-self.t0)
        pulse = (math.sin(elapsed * 6) + 1) / 2
        r=self.playing_board.radius
        for i in range(min(4, math.ceil(elapsed/self.highlight_time))):
            row, col = int(self.match[i][0]), int(self.match[i][1])
            x = self.playing_board.start_center[0]+col*self.playing_board.hori_centers
            y=self.playing_board.start_center[1]+row*self.playing_board.height_centers
            alpha = abs(int(60 + 80 * pulse))
            if self.board[row][col] == 1:
                self.playing_board.draw_piece(self.screen,(x,y),self.playing_board.piece1)
            elif self.board[row][col] == 2:
                self.playing_board.draw_piece(self.screen,(x,y),self.playing_board.piece2)
            glow_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            color=(0,230,200,alpha) if self.winner==1 else (210,225,225,alpha)
            pygame.draw.circle(glow_surf, color, (r, r), r)
            self.screen.blit(glow_surf, (x - r, y - r))    
        if elapsed>10*self.highlight_time:
            self.animate=False
    
    def turn_change(self,changed):
        if changed:
            if self.turn==1:
                self.turn=2
            else:
                self.turn=1



