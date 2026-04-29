import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__),'..'))
from game import Board
import pygame
import numpy as np
import time
import math

class draw:
    #the class which handles how to draw the screen with texts and buttons
    def __init__(self,width,height,screen,player1,player2):
        self.width=int(0.307*width)
        self.height=self.width
        self.color=(10,10,10)
        self.screen=screen
        self.padding=self.width*0.01
        self.cell_size=(self.width-self.padding*15)/10
        self.radius=int(self.cell_size*0.1)
        self.color1=(0, 229, 255)
        self.color2=(224, 64, 251)
        self.player1,self.player2=player1,player2
        self.player1cut,self.player2cut=self.player1,self.player2
        self.t0=None
        self.grid=pygame.Rect((width-self.width)/2+0.007*self.width,(height-self.height)/2+0.006*self.width,self.width,self.height)

    def crop_name(self, font, width, pnum, color): #to truncate the names to be displayed
        pnum=pnum-1 #converting to index
        name=[self.player1, self.player2][pnum]
        if font.size(name+'i')[0]>width: #the 'i' is to ensure text doesn't go too close to edge
            name_cut=[self.player1cut, self.player2cut][pnum]
            if font.size(name_cut+'i')[0]>width or font.size(name_cut+'i')[0]<width:
                lo, hi = 0, len(name) - 2  # -2 reserves room for ".."
                while lo < hi:
                    mid = (lo + hi + 1) // 2
                    if font.size(name[:mid] + "..")[0] <= width:
                        lo = mid
                    else:
                        hi = mid - 1
                name=name[:lo-1]+'...'
                if pnum==0: self.player1cut=name
                else: self.player2cut=name
        return font.render(f'{name}', True, color)

    def draw_board(self,info):
        #the function to draw the board
        pygame.draw.rect(self.screen,self.color,self.grid,border_radius=10)
        mx, my = pygame.mouse.get_pos()
        w,h=self.screen.get_size()
        pygame.draw.rect(self.screen,self.color1,
                        pygame.Rect(0.058*w,0.185*h,0.0745*h,0.0745*h),border_radius=5,width=3)
        pygame.draw.rect(self.screen,self.color2,
                         pygame.Rect(0.91*w,0.185*h,0.0745*h,0.0745*h),border_radius=5,width=3)
        self.draw_x(self.screen,pygame.Rect(0.058*w,0.185*h,0.0745*h,0.0745*h),self.color1)
        self.draw_o(self.screen,pygame.Rect(0.91*w,0.185*h,0.0745*h,0.0745*h),self.color2)
        font=pygame.font.SysFont("Consolas",int(20/800*w),bold=True)
        txt=font.render("PLAYER 1",True,self.color1)
        self.screen.blit(txt,pygame.Rect(0.1269*w,0.141*h,0,0))
        #txt=font.render(self.player1,True,self.color1)
        txt=self.crop_name(font, 0.1269*w, 1, self.color1)
        self.screen.blit(txt,pygame.Rect(0.1269*w,0.213*h,0,0))
        txt=font.render("PLAYER 2",True,self.color2)
        self.screen.blit(txt,pygame.Rect(0.8724*w-txt.get_width(),0.141*h,0,0))
        txt=self.crop_name(font, 0.1269*w, 2, self.color2)
        self.screen.blit(txt,pygame.Rect(0.8724*w-txt.get_width(),0.213*h,0,0))
        if self.t0==None:
            self.t0=time.time()
        elapsed=time.time()-self.t0
        formatted = time.strftime("%H:%M:%S", time.gmtime(elapsed))
        samay=font.render(formatted,True,(160,100,4))
        self.screen.blit(samay,pygame.Rect(w//2-samay.get_width()//2,0.9056*h,0,0))
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
        #draws the x piece
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
        #draws the o piece
        x,y,radius,_=rect
        radius=radius//2
        x+=radius
        y+=radius
        radius=int(radius*0.6)
        pygame.draw.circle(surface, color, (x, y), radius, max(1,int(6/18*radius)))
        pygame.draw.circle(surface, (240,240,255), (x, y), radius, max(int(2/18*radius),1))

class Tictactoe(Board):
    #the main class
    def __init__(self,width,height,screen,player1,player2):
        super().__init__(player1, player2, width, height, stats=None, screen=screen)
        self.player1,self.player2=player1,player2
        self.playing_board=draw(width,height,screen,self.player1,self.player2)
        self.board=np.zeros((10,10))
        self.screen=screen
        self.turn=1
        self.animate=False
        self.prev_animate=False
        self.t0=None
        self.highlight_time=0.3
        self.winner=0
        self.match=None
        self.p1resign=False
        self.p2resign=False
        self.quitted=False
        self.turnanim=False
        self.t0turn=None
        self.turnlength=0.3*width
        self.turn_dur=0.2
    def maximize(self,width,height,screen):
        t0=self.playing_board.t0
        self.playing_board=draw(width,height,screen,self.player1,self.player2)
        self.playing_board.t0=t0
        self.playing_board.draw_board(self.board)
        self.screen=screen
        self.turnlength=0.3*width
    def reset(self):
        self.board=np.zeros((10,10))
    def play(self, turn, event=None):
        w,h=self.screen.get_width(),self.screen.get_height()
        self.playing_board.draw_board(self.board)  # always redraw full board
        v=0.4*h
        if self.turnanim:
            #print("here")
            elapsed=time.time()-self.t0turn
            if elapsed>self.turn_dur:
                self.turnanim=False
                self.t0turn=None
                return
            l=self.turnlength*(1-elapsed/self.turn_dur)**2
            if self.turn==1:
                pygame.draw.line(self.screen,(255,0,160),(w,v),(w-l,v),5)
                pygame.draw.line(self.screen,(0,245,255),(0,v),(self.turnlength-l,v),5)
            elif self.turn==2:
                pygame.draw.line(self.screen,(0,245,255),(0,v),(l,v),5)
                pygame.draw.line(self.screen,(255,0,160),(w,v),(w-self.turnlength+l,v),5)
            temp=super().option_screen(0.13*w,0.0827*h,(0.0156*w,0.893*h),event)
            return False
        else:
            if self.turn==1:
                pygame.draw.line(self.screen,(0,245,255),(0,v),(self.turnlength,v),5)
            elif self.turn==2:
                pygame.draw.line(self.screen,(255,0,160),(w,v),(w-self.turnlength,v),5)
            temp=super().option_screen(0.13*w,0.0827*h,(0.0156*w,0.893*h),event)
        if type(temp)!=bool:
            if temp==1:
                self.p1resign=True
            elif temp==2:
                self.p2resign=True
            else:
                self.quitted=True
            return False
        if temp:
            return False

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
        if self.animate==False and self.prev_animate==False:
            if self.check_hori_vert(turn):
                self.t0=None
                self.winner=turn
            if self.check_diagonal(turn):
                self.t0=None
                self.winner=turn
            if self.check_draw():
                self.t0=None
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
        h = mask[:, 0:6] + mask[:, 1:7] + mask[:, 2:8] + mask[:, 3:9] + mask[:, 4:10]
        
        # Vertical: same but along rows
        v = mask[0:6, :] + mask[1:7, :] + mask[2:8, :] + mask[3:9, :] + mask[4:10, :]

        if bool((h >= 5).any()):
            row,col=np.where(h==5)
            row=row[0]
            col=col[0]
            self.match=np.stack((np.ones(5)*row,np.arange(col,col+5)),axis=1)
            self.animate=True
            return True
        elif bool((v>=5).any()):
            row,col=np.where(v==5)
            row=row[0]
            col=col[0]
            self.match=np.stack((np.arange(row,row+5),np.ones(5)*col),axis=1)
            self.animate=True
            return True
        return False        
        
    def check_diagonal(self,turn):
        mask = (self.board == turn).astype(int)

        # Main diagonal (top-left to bottom-right): shift down+right
        d1 = (mask[0:6, 0:6] + mask[1:7, 1:7] + mask[2:8, 2:8] + 
            mask[3:9, 3:9] + mask[4:10, 4:10])

        # Anti diagonal (top-right to bottom-left): shift down+left
        d2 = (mask[0:6, 4:10] + mask[1:7, 3:9] + mask[2:8, 2:8] + 
            mask[3:9, 1:7] + mask[4:10, 0:6])

        if bool((d1 >= 5).any()):
            row,col=np.where(d1==5)
            row=row[0]
            col=col[0]
            self.match=np.stack((np.arange(row,row+5),np.arange(col,col+5)),axis=1)
            self.animate=True
            return True
        elif bool((d2>=5).any()):
            row,col=np.where(d2==5)
            row=row[0]
            col=col[0]+4
            self.match=np.stack((np.arange(row,row+5),np.arange(col,col-5,-1)),axis=1)
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

        for i in range(min(5, math.ceil(elapsed/self.highlight_time))):
            row, col = int(self.match[i][0]), int(self.match[i][1])
            x = self.playing_board.padding*3 + col * (self.playing_board.cell_size + self.playing_board.padding) + self.playing_board.grid.x
            y = self.playing_board.padding*3 + row * (self.playing_board.cell_size + self.playing_board.padding) + self.playing_board.grid.y
            rect = pygame.Rect(x, y, self.playing_board.cell_size, self.playing_board.cell_size)
            alpha = abs(int(60 + 80 * pulse))
            glow_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            highlight_color=(*self.playing_board.color1, alpha) if self.winner==1 else (*self.playing_board.color2, alpha)
            pygame.draw.rect(glow_surface,(highlight_color),glow_surface.get_rect(),border_radius=self.playing_board.radius)
            self.screen.blit(glow_surface, rect.topleft)
            if self.board[row][col] == 1:
                self.playing_board.draw_x(self.screen, rect, self.playing_board.color1)
            elif self.board[row][col] == 2:
                self.playing_board.draw_o(self.screen, rect, self.playing_board.color2)    
        if elapsed>10*self.highlight_time:
            self.animate=False
        
    def turn_change(self,changed):
        if self.animate:
            self.turn=0
            return
        if changed:
            self.turnanim=True
            self.t0turn=time.time()
            if self.turn==1:
                self.turn=2
            else:
                self.turn=1
        




