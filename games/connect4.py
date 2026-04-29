import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__),'..'))
from game import Board
import pygame
import numpy as np
import time
import math

class draw:
    #draws the screen
    def __init__(self, width, height, screen,name1,name2):
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
        self.name1=name1
        self.name2=name2
        self.name1cut,self.name2cut=self.name1,self.name2
        self.pointer_size=0.01*width
        self.t0=0
        self.pointer_animate=False
        self.pointer_duration=0.2

    def crop_name(self, font, width, pnum, color):
        #crops the names
        width=width*0.8
        pnum=pnum-1 #converting to index
        name=[self.name1, self.name2][pnum]
        if font.size(name+'i')[0]>width: #the 'i' is to ensure text doesn't go too close to edge
            name_cut=[self.name1cut, self.name2cut][pnum]
            if font.size(name_cut+'i')[0]>width or font.size(name_cut+'i')[0]<width:
                lo, hi = 0, len(name) - 2  # -2 reserves room for ".."
                while lo < hi:
                    mid = (lo + hi + 1) // 2
                    if font.size(name[:mid] + "..")[0] <= width:
                        lo = mid
                    else:
                        hi = mid - 1
                name=name[:lo-1]+'...'
                if pnum==0: self.name1cut=name
                else: self.name2cut=name
        return font.render(f'{name}', True, color)


    def draw_board(self, info,event):
        #draws the board actually
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
        font=pygame.font.SysFont("Consolas",int(min(35/1919*self.width,35/982*self.height)),bold=True)
        txt1=self.crop_name(font, self.player1.get_width(), 1, (94,46,6))
        txt2=self.crop_name(font, self.player2.get_width(), 2, (94,46,6))
        self.screen.blit(txt1,(int(0.0743*self.width),int(0.3867*self.height)))
        self.screen.blit(txt2,(int(0.932267*self.width)-txt2.get_width(),int(0.3867*self.height)))
        tx,ty=pygame.mouse.get_pos()
        tx=max(min(tx,self.start_center[0]+6*self.hori_centers),self.start_center[0])
        ty=self.start_center[1]-self.height_centers
        s  = self.pointer_size
        if event!=None and event.type==pygame.MOUSEBUTTONDOWN:
            self.t0=time.time()
            self.pointer_animate=True
        elapsed=0
        if self.pointer_animate:
            elapsed=time.time()-self.t0
            s=s*(1+0.5*math.sin(math.pi*elapsed/self.pointer_duration))
        if elapsed>=self.pointer_duration:
            self.pointer_animate=False
        pts = [(tx,ty),(tx - s, ty-s),(tx + s, ty-s),]
        pygame.draw.polygon(self.screen, (0,0,0), pts)
        pygame.draw.polygon(self.screen, (0,0,0), pts,width=int(0.2*self.pointer_size))

    def draw_piece(self, surface, center, piece):
        #pastes the suitable picture for piece
        surface.blit(piece,(center[0]-self.radius,center[1]-self.radius))


class Connect4(Board):
    #the main class
    def __init__(self,width,height,screen,name1,name2):
        super().__init__(name1, name2, width, height, stats=None, screen=screen)
        self.playing_board=draw(width,height,screen,name1,name2)
        self.board=np.zeros((7,7))
        self.screen=screen
        self.turn=1
        self.animate=False
        self.prev_animate=False
        self.winner=0
        self.highlight_time=0.3
        self.name1=name1
        self.name2=name2
        self.drop_anim = None
        self.DROP_SPEED = 7  # rows per second
        self.p1resign=False
        self.p2resign=False
        self.quitted=False
        self.style=((232,164,74),(14,10,5),(122,78,26),(232,164,74),(139,94,42),(30,18,8))

    def maximize(self,width,height,screen):
        self.playing_board=draw(width,height,screen,self.name1,self.name2)
        self.playing_board.draw_board(self.board,None)
        self.screen=screen

    def reset(self):
        self.board=np.zeros((7,7))
        self.drop_anim = None

    def _col_from_mx(self, mx):
        """Return board column (0-6) for screen x, or -1 if outside the grid."""
        pb = self.playing_board
        for i in range(7):
            x = pb.start_center[0] - pb.hori_centers // 2 + i * pb.hori_centers
            y = pb.start_center[1] - pb.height_centers // 2
            if pygame.Rect(x, y, pb.hori_centers, pb.height_centers * 7).collidepoint(mx, pb.start_center[1]):
                return i
        return -1

    def play(self, turn, event=None):
        w,h=self.screen.get_width(),self.screen.get_height()
        self.playing_board.draw_board(self.board,event)  # always redraw full board
        temp=super().option_screen(0.13*w,0.0827*h,(0.0156*w,0.893*h),event,self.style)
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
        mx, my = pygame.mouse.get_pos()
        self.playing_board.pointer_col = -1 if self.drop_anim is not None else self._col_from_mx(mx)

        if self.drop_anim is not None:
            self.playing_board.draw_board(self.board,event)
            return self.tick_drop()

        self.playing_board.draw_board(self.board,event)

        if event and event.type == pygame.MOUSEBUTTONDOWN and not self.animate:
            col = self._col_from_mx(event.pos[0])
            if col != -1:
                row = -1
                for i in range(6, -1, -1):
                    if self.board[i][col] == 0:
                        row = i
                        break
                if row != -1:
                    pb = self.playing_board
                    y_start = float(pb.start_center[1])
                    y_end   = float(pb.start_center[1] + row * pb.height_centers)
                    duration = max(row / self.DROP_SPEED, 0.05)
                    self.drop_anim = {
                        'col': col, 'row': row, 'turn': turn,
                        'y_start': y_start, 'y_end': y_end,
                        't0': time.time(), 'duration': duration
                    }
        return False

    def tick_drop(self):
        da = self.drop_anim
        pb = self.playing_board
        elapsed = time.time() - da['t0']
        t = min(elapsed / da['duration'], 1.0)
        t_eased = 1 - (1 - t) ** 2

        y_cur = da['y_start'] + (da['y_end'] - da['y_start']) * t_eased
        x = pb.start_center[0] + da['col'] * pb.hori_centers
        piece = pb.piece1 if da['turn'] == 1 else pb.piece2
        pb.draw_piece(self.screen, (int(x), int(y_cur)), piece)

        if t >= 1.0:
            self.board[da['row']][da['col']] = da['turn']
            self.drop_anim = None
            return True
        return False

    def win_check(self,turn):
        if self.animate==False and self.prev_animate==False:
            if self.check_hori_vert(turn):
                self.playing_board.draw_board(self.board,None)
                self.winner=turn
            if self.check_diagonal(turn):
                self.playing_board.draw_board(self.board,None)
                self.winner=turn
            if self.check_draw():
                self.playing_board.draw_board(self.board,None)
                return 0
        elif self.animate==True:
            self.highlight()
            self.prev_animate=True
        elif self.animate==False and self.prev_animate==True:
            return self.winner
        return "none"

    def check_hori_vert(self,turn):
        mask = (self.board == turn).astype(int)
        h = mask[:, 0:4] + mask[:, 1:5] + mask[:, 2:6] + mask[:,3:7]
        v = mask[0:4, :] + mask[1:5, :] + mask[2:6, :] + mask[3:7, :]

        if bool((h >= 4).any()):
            row,col=np.where(h==4)
            row=row[0]; col=col[0]
            self.match=np.stack((np.ones(4)*row,np.arange(col,col+4)),axis=1)
            self.animate=True
            return True
        elif bool((v>=4).any()):
            row,col=np.where(v==4)
            row=row[0]; col=col[0]
            self.match=np.stack((np.arange(row,row+4),np.ones(4)*col),axis=1)
            self.animate=True
            return True
        return False        
        
    def check_diagonal(self,turn):
        mask = (self.board == turn).astype(int)
        d1 = (mask[0:4, 0:4] + mask[1:5, 1:5] + mask[2:6, 2:6] + mask[3:7, 3:7])
        d2 = (mask[0:4, 3:7] + mask[1:5, 2:6] + mask[2:6, 1:5] + mask[3:7, 0:4])

        if bool((d1 >= 4).any()):
            row,col=np.where(d1==4)
            row=row[0]; col=col[0]
            self.match=np.stack((np.arange(row,row+4),np.arange(col,col+4)),axis=1)
            self.animate=True
            return True
        elif bool((d2>=4).any()):
            row,col=np.where(d2==4)
            row=row[0]; col=col[0]+3
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
    
    def turn_change(self, changed):
        if changed:
            if self.turn==1:
                self.turn=2
            else:
                self.turn=1
