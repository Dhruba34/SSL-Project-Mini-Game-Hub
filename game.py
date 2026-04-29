import pygame
import numpy as np
import time
import os
import sys
import matplotlib.pyplot as plt
import math

class TransitionManager:#Manages the fading in and out of screen
    GAME_NAMES  = {0: "TIC TAC TOE", 1: "OTHELLO", 2: "CONNECT 4"}
    GAME_COLORS = {0: (0, 200, 255), 1: (180, 100, 255), 2: (255, 140, 0)}

    def __init__(self, screen):
        self.screen=screen#the current screen
        self.state="idle"#records the phase in which the animation is
        self.t0=0.0#to keep record of the initial timestamp. however it will be reassigned again while fading out
        self.game= 0
        self.snapshot=None#to have a screenshot of the screen last seen before fading in
        self.just_finished=False#indicator of whether 
        self.fade_duration=0.5#duration of fading out when new screen appears
        self.show_duration=3.6#duration of fading in when darkness appears
        self.reveal_duration=5.1#duration of stopping for a moment in darkness and showing some animation
        self.reveal_img=""#the image which will be slowly appearing
        self.board=None

    def start(self, game_index,reveal_img,board):#the function for starting of darkness increasing slowly
        self.game=game_index
        self.t0=time.time()#noting the starting time
        self.state="fade_out"#this phase is named as fade_out. well yaa I often confuse fade in and fade out. I shoulv'e used better terminology
        self.snapshot=self.screen.copy()#getting a screenshot of the screen
        self.reveal_img=reveal_img
        self.board=board

    def active(self):
        return self.state != "idle"

    @property
    def done(self):#just an easy way to check that if our whole animation is finished or not
        return self.state == "idle" and self.just_finished

    def _overlay(self, w, h, alpha):#the dark screen which is overlayed on snapshot
        s = pygame.Surface((w, h))
        s.fill((0, 0, 0))
        s.set_alpha(alpha)
        self.screen.blit(s, (0, 0))

    def update(self):
        self.just_finished = False
        if self.state == "idle":
            return
        now, elapsed = time.time(), time.time() - self.t0#getting the current time and time passed since animation started
        w, h = self.screen.get_size()

        if self.state == "fade_out":#this is the first phase of animation
            if self.snapshot:#if something is there in snapshot then blit it
                self.screen.blit(pygame.transform.scale(self.snapshot, (w, h)), (0, 0))
            self._overlay(w, h, int(255 * min(elapsed / self.fade_dur, 1.0)))#updon the snapshot, the dark screen with increasing alpha is overlayed
            if elapsed >= self.fade_dur:#if time is up for fade_out then the phase is shifted and time is counted for this phase
                self.t0, self.state = now, "show"

        elif self.state == "show":#the second phase of animation
            self._draw_splash(w, h, elapsed)#the function to draw the horizontal bars and the blinking texts
            if elapsed >= self.reveal_dur:#
                self.t0, self.state = now, "fade_in"
                self.snapshot  = pygame.image.load(self.reveal_img)#here the snapshot is replaced and then snapshot will be slowly revealed
                self.board.bg  = pygame.transform.scale(
                    pygame.image.load(self.reveal_img),
                    (self.board.width, self.board.height)
                )

        elif self.state == "fade_in":#the last phase of animation
            self._overlay(w, h, int(255 * (1 - min(elapsed / self.fade_dur, 1))))
            if elapsed >= self.fade_dur:#if time is up then phase returns to idle state
                self.state, self.just_finished = "idle", True

    def _draw_splash(self, w, h, elapsed):#the function to draw the screen during the 2nd state
        accent = self.GAME_COLORS[self.game]
        name   = self.GAME_NAMES[self.game]

        # Background grid
        self.screen.fill((0, 0, 0))
        for y in range(0, h, 18):
            pygame.draw.line(self.screen, (10, 10, 10), (0, y), (w, y), 1)
        for x in range(0, w, 36):
            pygame.draw.line(self.screen, (8, 8, 8), (x, 0), (x, h), 1)

        # Pulsing horizontal bars
        bar = pygame.Surface((w, 3), pygame.SRCALPHA)
        bar.fill((*accent, int(80 + 60 * math.sin(elapsed * 3.0))))
        for dy in (int(-60/400*h), int(60/400*h)):
            self.screen.blit(bar, (0, h // 2 + dy))

        # Corner brackets
        bk  = pygame.Surface((w, h), pygame.SRCALPHA)
        arm = 22
        c   = (*accent, min(255, int(255 * elapsed / 0.2)))
        m   = 24
        for (cx, cy), (dx, dy), (ex, ey) in [
            ((m,   m),   (1,0),  (0,1)),
            ((w-m, m),  (-1,0),  (0,1)),
            ((m,   h-m), (1,0),  (0,-1)),
            ((w-m, h-m),(-1,0),  (0,-1)),
        ]:
            pygame.draw.line(bk, c, (cx, cy), (cx+dx*arm, cy+dy*arm), 2)
            pygame.draw.line(bk, c, (cx, cy), (cx+ex*arm, cy+ey*arm), 2)
        self.screen.blit(bk, (0, 0))

        # Main text
        reveal_frac  = min(elapsed / self.reveal_dur, 1.0)
        visible      = name[:int(len(name) * reveal_frac)]
        cursor       = "_" if len(visible) < len(name) else ""
        font_size    = max(28, min(72, int(w * 0.075)))
        try:    font = pygame.font.SysFont("Consolas", font_size, bold=True)
        except: font = pygame.font.Font(None, font_size)

        glow = font.render(visible + cursor, True, tuple(max(0, c - 100) for c in accent))
        txt  = font.render(visible + cursor, True, accent)
        gx   = (w - txt.get_width()) // 2

        if reveal_frac < 1.0:
            # Only title — vertically centered alone
            gy = h // 2 - txt.get_height() // 2
            for ox, oy in [(-2,0),(2,0),(0,-2),(0,2)]:
                self.screen.blit(glow, (gx+ox, gy+oy))
            self.screen.blit(txt, (gx, gy))
        else:
            # Title + subtitle — centered together as a block
            sub_font  = pygame.font.SysFont("Consolas", max(12, font_size // 4))
            sub       = sub_font.render("LOADING BOARD...", True, accent)
            sub_alpha = int(255 * min((elapsed - self.reveal_dur) / 0.3, 1.0))
            sub_surf  = pygame.Surface((sub.get_width(), sub.get_height()), pygame.SRCALPHA)
            sub_surf.blit(sub, (0, 0))
            sub_surf.set_alpha(sub_alpha)

            gap       = int(h*0.03)
            total_h   = txt.get_height() + gap + sub.get_height()
            gy        = h // 2 - total_h // 2

            for ox, oy in [(-2,0),(2,0),(0,-2),(0,2)]:
                self.screen.blit(glow, (gx+ox, gy+oy))
            self.screen.blit(txt, (gx, gy))
            self.screen.blit(sub_surf, ((w - sub.get_width()) // 2, gy + txt.get_height() + gap))

#the class for button
class Button:
    def __init__(self, text, x, y, w, h, font,offset=0,style=None):
        self.rect = pygame.Rect(x, y, w, h) #just an aggregation of x,y,w,h to get the box for button
        self.text = text#text to be displayed inside button
        self.font = font#font of text inside button
        self.hovered = False#indicator for whether mouse is hovering on button or not
        if style==None:#style sets the colour of the button according to the theme
            self.accent = (0,200,255)#for the text inside
            self.bg     = (0,13,26)#for the panel of the button
            self.dim    = (26,96,144)#for the slight boundary colour of the button
        else:
            self.accent,self.bg,self.dim=style[0],style[1],style[2]
        self.offset=offset#for offsetting the text horizontally from the center of the button

    def assign(self, text, x, y, w, h, font,offset=0,style=None):#just a function to set parameters without making new objects
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = font
        self.offset=offset
        if style==None:
            self.accent = (0,200,255)
            self.bg     = (0,13,26)
            self.dim    = (26,96,144)
        else:
            self.accent,self.bg,self.dim=style[0],style[1],style[2]

    def handle_event(self, event):#the function which returns True when button is clicked and manages the hovering effect for button
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    def polygon(self):#helper function for making polygon according to the class variables
        x, y, w, h = self.rect
        notch=int(12/45*h)
        return [
            (x + notch, y),
            (x + w,     y),
            (x + w,     y + h),
            (x,         y + h),
            (x,         y + notch),
        ]

    def draw(self,screen):#actually draws the button
        x,y,w,h=self.rect
        notch=int(12/45*h)
        accent=self.accent
        dim=self.dim
        poly=self.polygon()
        local_poly=[(px-x,py-y) for px,py in poly]
        bg_surf=pygame.Surface((w,h),pygame.SRCALPHA)
        pygame.draw.polygon(bg_surf,(*self.bg,230),local_poly)#draws the polygon which is the boundary of the button on a surface
        screen.blit(bg_surf,(x,y))#button on a dummy screen and then on screen to enable transparency and hence good effects
        pulse=0.55
        border_color=tuple(int(c*pulse) for c in dim) if not self.hovered else accent #making the difference between hovering and not hovering
        border_alpha=255 if self.hovered else int(180*pulse) #if hovered then full solid panel color
        border_surf=pygame.Surface((w,h),pygame.SRCALPHA)
        pygame.draw.polygon(border_surf,(*border_color,border_alpha),local_poly,2)
        screen.blit(border_surf,(x,y))
        if self.hovered:
            hover_surf=pygame.Surface((w,h),pygame.SRCALPHA)
            pygame.draw.polygon(hover_surf,(*accent,18),local_poly)
            screen.blit(hover_surf,(x,y))
        else:
            pygame.draw.line(screen,(*dim,180),(x,y+notch),(x+notch,y),2)
            pygame.draw.line(screen,(*dim,180),(x,y+notch),(x,y+h//2+notch//2),1)
        #in total there are 3 surfaces which handle the appearance between hovering and  not hovering
        text_color=(255,255,255) if self.hovered else accent#total white if hovered
        txt=self.font.render(self.text,True,text_color)
        screen.blit(txt,(x+(w-txt.get_width())//2+self.offset,y+(h-txt.get_height())//2))

#the class for making checkboxes
class Checkbox:
    def __init__(self, x, y, rect_width,text,idx,font_name="Consolas", radius=10):
        #x,y are the positions
        self.x = x
        self.y = y
        #the displaywidth is kind of useless but rect_width is useful in determining font_size 
        self.displaywidth=rect_width
        self.text = text
        font_size=int(9/320*rect_width)
        self.font = pygame.font.SysFont(font_name, font_size)
        self.font_box=pygame.font.SysFont(font_name,18)
        self.radius = radius#the radius of the radio button
        self.selected = False#stores whether checkbox is selected
        self.idx=idx#id of the checkbox
        self.reverse=False#stores if radiobutton is selected or not
        self.rect=None
        self.priority=0#stores the priority of this checkbox necessary for leaderboard
        self.radiorect=None

    def assign(self,x,y,rect_width,text,font_name="Consolas"):
        self.x = x
        self.y = y
        self.displaywidth=rect_width
        self.text = text
        font_size=int(12/320*rect_width)
        self.font = pygame.font.SysFont(font_name, font_size)
        self.font_box=pygame.font.SysFont(font_name,int(0.75*font_size))
        self.radius = self.font.render("a",True,(0,0,0)).get_height()//2

    def select(self):#marks the checkbox selected
        self.selected = True

    def deselect(self):#marks the checkbox unselected
        self.selected = False

    def draw(self, screen,style=None):#draws the checkbox, text and radiobutton
        r   = self.radius
        accent=(0,180,255) if style==None else style[3]
        border=(0,100,200) if style==None else style[4]
        panel=(4,18,40) if style==None else style[5]
        box = pygame.Rect(self.x - r, self.y - r, r * 2, r * 2)
        glow_alpha = 180 if self.selected else 60
        for spread in (r + 6, r + 4, r + 2):
            glow_surf = pygame.Surface((spread * 2, spread * 2), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*accent, glow_alpha // (spread - r + 1)),
                             (0, 0, spread * 2, spread * 2), border_radius=4)
            screen.blit(glow_surf, (self.x - spread, self.y - spread))
        if self.selected:
            pygame.draw.rect(screen, (border[0]*0.6,0.6*border[1],0.6*border[2]), box, border_radius=3)
        else:
            pygame.draw.rect(screen, panel, box, border_radius=3)

        pygame.draw.rect(screen, (accent[0],accent[1]*7/9,accent[2]*220/255), box, 1, border_radius=3)
        if self.selected:
            badge_font = self.font_box
            num = badge_font.render(str(self.priority), True, (accent[0],accent[1]*220/180,accent[2]))
            screen.blit(num, (box.center[0] - num.get_width()//2, box.center[1]-num.get_height()//2))
        col=(180,220,255) if style==None else (220,255,180) #toggled between two themes of by the style parameter
        text_col = col if self.selected else (border[1]*0.6,border[1],border[2]*16/22)
        text_surf = self.font.render(self.text, True, text_col)
        tx = self.x + r + 10
        ty = self.y - text_surf.get_height() // 2
        screen.blit(text_surf, (tx, ty))
        self.rect = pygame.Rect(self.x - r, self.y - r,
                                r * 2 + 10 + text_surf.get_width(),
                                max(r * 2, text_surf.get_height()))
        rx = int(self.x + self.displaywidth * 0.8)
        ry = self.y
        radio_r = self.radius
        if self.reverse:
            for spread in (radio_r + 5, radio_r + 3):
                gs = pygame.Surface((spread * 2, spread * 2), pygame.SRCALPHA)
                pygame.draw.circle(gs, (accent[0],border[1]*20/18,accent[2], 40), (spread, spread), spread)
                screen.blit(gs, (rx - spread, ry - spread))

        pygame.draw.circle(screen, panel, (rx, ry), radio_r)
        pygame.draw.circle(screen, (accent[0],accent[1]*7/9,accent[2]), (rx, ry), radio_r, 1)

        if self.reverse:
            pygame.draw.circle(screen, (accent[0],accent[1]*220/180,accent[2]), (rx, ry), radio_r // 2)

        self.radiorect = pygame.Rect(rx - radio_r, ry - radio_r,
                                     radio_r * 2, radio_r * 2)


class Menu:#the class for drawing the menu
    def __init__(self,width,height,board):
        self.width=width
        self.height=height
        self.board=board
        #defines the fonts and 3 buttons
        self.font=pygame.font.SysFont("Consolas",int(min(18/800*width,18/400*height)))
        self.font2=pygame.font.SysFont("Consolas",int(min(30/800*width,30/400*height)))
        self.tictactoe=Button("TicTacToe",0.4*width,0.35*height,0.2*width,0.1125*height,self.font)
        self.othello=Button("Othello",0.4*width,0.51875*height,0.2*width,0.1125*height,self.font)
        self.connect4=Button("Connect4",0.4*width,0.6875*height,0.2*width,0.1125*height,self.font)

    def draw(self,screen,event):
        #sets the background for the menu screen
        board.bg=pygame.transform.scale(pygame.image.load("./pictures/background4.png"),(self.width,self.height))
        #draws all the three buttons
        self.tictactoe.draw(screen)
        self.othello.draw(screen)
        self.connect4.draw(screen)
        #set the title for the page
        title=self.font2.render("SELECT GAME",True,(235, 205, 205))
        screen.blit(title,pygame.Rect(0.38125*self.width,0.2*self.height,0.3*self.width,0.1*self.height))
        #handled the clicking events of the three buttons
        if self.tictactoe.handle_event(event):
            return 0
        elif self.othello.handle_event(event):
            return 1
        elif self.connect4.handle_event(event):
            return 2
        else:
            return 3


class Board:# the main class
    _C_PANEL    = (4,   18,  40)   # panel surface
    _C_BORDER   = (0,  100, 200)   # accent border
    _C_ACCENT   = (0,  180, 255)   # bright cyan-blue

    def __init__(self,player1,player2,width,height,screen=None):
        #player names
        self.player1=player1
        self.player2=player2
        if screen==None:
            self.screen=pygame.display.set_mode((width,height),pygame.RESIZABLE)
        else:
            self.screen=screen
        self.width=width
        self.height=height
        #image is loaded by default
        self.bg=pygame.image.load("./pictures/background4.png")
        self.bg=pygame.transform.scale(self.bg,(self.width,self.height))
        self.board=None
        #the checkboxes for the leaderboard
        self.o1=Checkbox(0,0,0,"",1)
        self.o2=Checkbox(0,0,0,"",2)
        self.o3=Checkbox(0,0,0,"",3)
        self.o4=Checkbox(0,0,0,"",4)
        self.o5=Checkbox(0,0,0,"",5)
        self.o6=Checkbox(0,0,0,"",6)
        self.o7=Checkbox(0,0,0,"",7)
        #the default priority order for the leaderboard
        self.default=[1,2,3,4,5,6,7]
        #the buttons present in the leaderboard screen
        self.ldb_but=Button("",0,0,0,0,None)
        self.charts=Button("",0,0,0,0,None)
        #to track whether matplotlib is closed or not
        self.fig_no=0
        #buttons for the final screen
        self.b1=Button("",0,0,0,0,None)
        self.b2=Button("",0,0,0,0,None)
        #variable for storing the priorities for the selected checkboxes in the leaderboard screen
        self.priorities=[]
        self.transition = TransitionManager(self.screen)
        self.t0=None
        self.snapshot=None
        #options for the options button
        self.options=Button("",0,0,0,0,None)
        self.resign1=Button("",0,0,0,0,None)
        self.resign2=Button("",0,0,0,0,None)
        self.quit=Button("",0,0,0,0,None)
        self.resume=Button("",0,0,0,0,None)
        #flag showing whether options screen should be displayed or not
        self.showing_options=False
        #toggle to display charts on separate screen or not
        self.show=True
        #variable to store whether exit is clicked or menu in self.show=False case
        self.chartsbut=0

    def draw_corner_brackets(self, surf, rx, ry, rw, rh, arm=18, color=None, alpha=255, thick=2): #designing purpose for fancy screen
        color = color or self._C_ACCENT
        s = pygame.Surface((rw, rh), pygame.SRCALPHA)
        c = (*color, alpha)
        corners = [
            ((0,    0),    (1, 0),  (0,  1)),
            ((rw-1, 0),   (-1, 0),  (0,  1)),
            ((0,    rh-1), (1, 0),  (0, -1)),
            ((rw-1, rh-1),(-1, 0),  (0, -1)),
        ]
        for (cx, cy), (dx, dy), (ex, ey) in corners:
            pygame.draw.line(s, c, (cx, cy), (cx + dx*arm/800*self.width, cy + dy*arm/400*self.height), thick)
            pygame.draw.line(s, c, (cx, cy), (cx + ex*arm/800*self.width, cy + ey*arm/400*self.height), thick)
        surf.blit(s, (rx, ry))

    def draw_hbar(self, surf, x, y, w, glow_alpha=60,accent=_C_ACCENT,border=_C_BORDER):#designing purpose for fancy screen
        """Horizontal rule with a short bright left cap."""
        color = accent
        dim   = (0.6*border[0],0.6*border[1],0.6*border[2])
        pygame.draw.line(surf, dim, (x, y), (x + w, y), 1)
        cap = min(w, 80)
        for i in range(4, 0, -1):
            s = pygame.Surface((cap, 2+i), pygame.SRCALPHA)
            s.fill((*color, glow_alpha // i))
            surf.blit(s, (x, y - 1))
        pygame.draw.line(surf, color, (x, y), (x + cap, y), 1)

    def glow_text(self, surf, font, text, color, x, y, spread=3, glow_alpha=40):#designing purpose for fancy screen
        """Blit text with a soft outer glow."""
        glow_col = tuple(min(255, int(c * 0.6)) for c in color)
        glow_s   = font.render(text, True, glow_col)
        glow_s.set_alpha(glow_alpha)
        for ox, oy in [(-spread,0),(spread,0),(0,-spread),(0,spread)]:
            surf.blit(glow_s, (x + ox, y + oy))
        main = font.render(text,True, color)
        surf.blit(main, (x, y))

    def page(self):#function to set the background
        self.screen.blit(self.bg,(0,0))
    def show_leaderboard(self,event,style=None):#to draw the leaderboard using fancy screen function. using modularity
        w,h=self.width,self.height
        if style==None:
            accent=(0,180,255)
        else:
            accent=style[3]

        #first the texts for fancy screen
        title=(pygame.font.SysFont("Consolas",int(w*0.0319), bold=True),"Sort Mode of Leaderboard",accent,0.2415*w,0.1146*h,True,0.00275*w,50)
        sec_font=pygame.font.SysFont("Consolas", int(w*0.0154))

        select=(sec_font,"SELECT  &  PRIORITISE  COLUMNS",accent,0.2415*w,0.254*h,False)
        txt=sec_font.render("REVERSE",True,(0,0,0))
        rev=(sec_font,"REVERSE",accent,0.742*w-txt.get_width(),0.254*h,False)


        #next the checkboxes for fancy screen
        cx=0.28*w
        row_y   = [0.31878*h,0.38356*h,0.44834*h,0.51312*h,0.5779*h,0.64268*h,0.70746*h]
        labels  = [
            "Game name lexicographically",
            "Username",
            "No. of Wins",
            "No. of Losses",
            "No. of Draws",
            "Win / Loss ratio",
            "No. of Games played of this type",
        ]
        objs    = [self.o1, self.o2, self.o3, self.o4,
                   self.o5, self.o6, self.o7]
        checks=[(cx,row_y[i],labels[i],objs[i]) for i in range(7)]

        #assigned the buttons for leaderboard
        self.ldb_but.assign("Generate",0.588*w,0.78044*h,0.165*w,0.0984*h,pygame.font.SysFont("Consolas", int(0.022*w), bold=True),style=style)
        self.charts.assign("Visualize",0.247*w,0.7804*h,0.165*w,0.0984*h,pygame.font.SysFont("Consolas", int(0.022*w), bold=True),style=style)

        #next the horizontal bars for fancy screen
        bars=[(0.2415*w,0.1146*h+title[0].get_height()*1.2,0.484*w),(0.247*w,0.74764*h,0.506*w)]
        #finally called fancy screen
        self.fancy_screen([title,select,rev],checks,bars,style)
        #drew the buttons
        self.ldb_but.draw(self.screen)
        self.charts.draw(self.screen)

        rects      = [o.rect      for o in objs]
        radiorects = [o.radiorect for o in objs]
        #event handling of buttons and checkboxes
        if event.type == pygame.MOUSEBUTTONDOWN:
            for i in range(7):
                if rects[i] and rects[i].collidepoint(event.pos):
                    if not objs[i].selected:
                        objs[i].selected = True
                        self.priorities.append(objs[i])
                    else:
                        objs[i].selected = False
                        self.priorities.remove(objs[i])
            for i in range(len(self.priorities)):
                self.priorities[i].priority = i + 1

            for i in range(7):
                if radiorects[i] and radiorects[i].collidepoint(event.pos):
                    objs[i].reverse = not objs[i].reverse

        if self.charts.handle_event(event):
            #if charts button pressed then returns True and later the charts section will be activated
            return True
        if self.ldb_but.handle_event(event):
            preference = [-o.idx if o.reverse else o.idx for o in self.priorities]
            arr=self.default
            for i in preference: arr.remove(abs(i))
            preference=preference+arr 
            #executing leaderboard.sh
            cmd = "bash leaderboard.sh"
            for i in preference:
                cmd += " " + str(i)
            print(cmd)
            os.system(cmd)
        return False


    def fancy_screen(self,texts,checks,bars,style=None):
        """
        Sci-fi redesign of the leaderboard sort-options page.
        All original logic (checkbox select/deselect, priority tracking,
        reverse radio, Generate + Visualize buttons) is unchanged.
        """
        w, h = self.screen.get_size()
        pw = int(w * 0.55)
        ph = int(h * 0.82)
        px = (w - pw) // 2
        py = (h - ph) // 2
        if style==None:
            accentc,borderc,panelc=self._C_ACCENT,self._C_BORDER,self._C_PANEL
        else:
            accentc,borderc,panelc=style[3],style[4],style[5]
            #style for the correct theme setting
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 6, 18, 210))#a dark screen overlayed on background
        self.screen.blit(overlay, (0, 0))
        panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
        panel.fill((*panelc, 245))
        self.screen.blit(panel, (px, py))
        glow_s = pygame.Surface((pw, ph), pygame.SRCALPHA)

        #multiple circles drawn for a glow type effect just a decoration
        for radius in range(int(120/400*self.height), 0, int(-20/400*self.height)):
            alpha = max(0, 18 - (120 - radius*400/self.height) // 6)
            pygame.draw.circle(glow_s, (*accentc, alpha),(pw - 40*400/self.height, 40*400/self.height), radius)
        self.screen.blit(glow_s, (px, py))
        pygame.draw.rect(self.screen, borderc,
                         (px, py, pw, ph), 1, border_radius=4)
        
        #corner brackets drawn
        self.draw_corner_brackets(self.screen, px, py, pw, ph,
                                   arm=16, color=borderc, alpha=200)
        
        #the texts are added to the screen
        for i in texts:
            if i[5]:
                self.glow_text(self.screen,*i[:5],spread=i[6],glow_alpha=i[7])
            else:
                self.glow_text(self.screen,*i[:-1])
        
        #the checkboxes are added to the screen
        for i in checks:
            obj=i[3]
            obj.assign(i[0], i[1], pw, i[2])
            if obj.selected:
                stripe = pygame.Surface((obj.radius*2.1,obj.radius*2.1),
                                        pygame.SRCALPHA)
                stripe.fill((*borderc, 18))
                self.screen.blit(stripe,(i[0]-obj.radius*1.05,i[1] - obj.radius*1.05))
            obj.draw(self.screen,style)

        #the horizontal bars are added to the screen
        for bar in bars:
            if style==None:
                self.draw_hbar(self.screen,*bar)
            else:
                self.draw_hbar(self.screen,*bar,accent=style[3],border=style[4])
        

    def draw_results(self, text, color=(171, 64, 2)):# method to draw the game over screen
        w, h = self.screen.get_size()
        elapsed = time.time() - self.t0 #elapsed calculated for blinking of text animation
        self.screen.blit(self.snapshot, (0, 0))
        fade = min(1, elapsed / 0.6)
        fade = fade * fade
        dark_alpha = int(200 * fade)
        bar_alpha  = int(180 * fade)
        dark = pygame.Surface((w, h), pygame.SRCALPHA)
        dark.fill((0, 0, 0, dark_alpha))
        self.screen.blit(dark, (0, 0))
        bar_height = int(0.20 * h)  #the gap between two horizontal bars
        bar_y = h // 2 - bar_height // 2
        for i in range(bar_height):
            t = abs(i - bar_height / 2) / (bar_height / 2)
            alpha = int(bar_alpha * (1 - t * t)) #the layered setting of the lines to make it much better in design
            line = pygame.Surface((w, 1), pygame.SRCALPHA)
            line.fill((0, 0, 0, alpha))
            self.screen.blit(line, (0, bar_y + i))
        def glow_line(y):
            for i in range(10, 0, -1):
                surf = pygame.Surface((w, 2), pygame.SRCALPHA)
                surf.fill((*color, 18 * i))
                self.screen.blit(surf, (0, y - i))
        glow_line(bar_y) #same layered appearance of line to make it better
        glow_line(bar_y + bar_height)  #again the same layered appearance
        font_size = int(h * 0.09)
        font = pygame.font.SysFont("Georgia", font_size, bold=True)
        txt  = font.render(text, True, color)
        while txt.get_width() > w * 0.85 and font_size > 20:  #formatting of text for a layered appearance
            font_size -= 2
            font = pygame.font.SysFont("Georgia", font_size, bold=True)
            txt  = font.render(text, True, color)
        tx = w // 2 - txt.get_width() // 2
        ty = h // 2 - txt.get_height() // 2

        #many screens are just pasted with varied alphas of the text for a better appearance
        for spread in range(6, 0, -2):
            glow_surf = font.render(text, True, color)
            glow_surf.set_alpha(30)
            self.screen.blit(glow_surf, (tx - spread, ty))
            self.screen.blit(glow_surf, (tx + spread, ty))
            self.screen.blit(glow_surf, (tx, ty - spread // 2))
            self.screen.blit(glow_surf, (tx, ty + spread // 2))
        self.screen.blit(txt, (tx, ty))
        font_small = pygame.font.SysFont("Consolas", int(h * 0.032))
        blink  = (math.sin(elapsed * 3) + 1) / 2
        alpha  = int(120 + 120 * blink)

        #text appears with varying alpha with time
        sub = font_small.render("Press SPACE to continue", True, (200, 200, 200))
        sub.set_alpha(alpha)
        sx = w // 2 - sub.get_width() // 2
        sy = bar_height * 1.1 + bar_y
        self.screen.blit(sub, (sx, sy))

    def show_results(self, winner, event): #the results are shown via draw_results
        self.options=None
        if self.t0 is None:
            self.t0 = time.time()
        if winner == 0:
            self.draw_results("DRAW")
        elif winner == 1:
            self.draw_results("WINNER: " + self.player1)
        else:
            self.draw_results("WINNER: " + self.player2)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                return True
        return False

    def draw_gauge(self, ax, values, texts, colors, title="", theme=1): #the gauges are drawn for matplotlib with varied theme
        gap = 80
        total_arc = 360 - gap
        start_angle = 90 + gap / 2
        filled_frac = [
            values["win"]  / values["games"],
            values["loss"] / values["games"],
            values["draw"] / values["games"],
        ]
        filled_deg = list(total_arc * np.array(filled_frac) / 360)
        ring_width = 0.28

        wedges, _ = ax.pie(
            filled_deg + [gap / 360],
            startangle=start_angle,
            colors=colors + ["none"],
            wedgeprops=dict(width=ring_width,
                            edgecolor="#1a0f08" if theme==1 else "#0a0015",
                            linewidth=1.5),
            counterclock=False,
        )

        if theme == 1:
            label_colors = ["#E8A44A", "#C0523A", "#6B9E7A"]
            title_color  = "#D4A868"
        else:
            label_colors = ["#00f5ff", "#ff00a0", "#b000ff"]
            title_color  = "#cc88ff"

        icons = ["▲", "▼", "—"] #proper labelling of text of gauges
        for i, (text, lc, icon) in enumerate(zip(texts, label_colors, icons)):
            offset = 0.28 * (i - (len(texts) - 1) / 2)
            ax.text(0, -offset - 0.04, f"{icon} {text}",
                    ha="center", va="center",
                    fontsize=9, fontweight="bold",
                    color=lc, fontfamily="monospace")

        if title:
            ax.text(0, -1.35, title,
                    ha="center", va="center",
                    fontsize=10, fontweight="bold",
                    color=title_color, fontfamily="monospace")
        ax.axis("off")

    def draw_charts(self, theme): #function just draw the pie charts and bar charts and give necessary details to draw_gauge for gauges
        stat_store = [
            {"games": 0, "win": 0, "loss": 0, "draw": 0},
            {"games": 0, "win": 0, "loss": 0, "draw": 0},
        ]
        win_players = {}
        game_counts = [0, 0, 0]


        #reading history.csv to find out wins losses most wins etc
        with open("history.csv", "r") as f:
            for line in f:
                arr = line.split(",")
                arr[6] = arr[6].removesuffix("\n")
                for idx, player in enumerate([self.player1, self.player2]):
                    if arr[1] == player or arr[2] == player:
                        stat_store[idx]["games"] += 1
                        if arr[0] == "DRAW":
                            stat_store[idx]["draw"] += 1
                        elif arr[3] == player:
                            stat_store[idx]["win"] += 1
                        else:
                            stat_store[idx]["loss"] += 1
                if arr[3] in win_players:
                    win_players[arr[3]] += 1
                elif arr[3] != "NA":
                    win_players[arr[3]] = 1
                if arr[6] == "TicTacToe":
                    game_counts[0] += 1
                elif arr[6] == "Othello":
                    game_counts[1] += 1
                else:
                    game_counts[2] += 1

        wingames = sorted(win_players.items(), key=lambda x: x[1], reverse=True)[:5]

        # ── Theme palettes ────────────────────────────────────────────
        if theme == 1:
            BG       = "#1a0f08"
            PANEL    = "#1e1208"
            ACCENT1  = "#E8A44A"   # copper
            ACCENT2  = "#C0523A"   # rust
            ACCENT3  = "#6B9E7A"   # patina teal
            MUTED    = "#8B6040"
            TEXT     = "#D4A868"
            GRID_COL = "#2a1c0e"
            TITLE    = "GAME  POINT  —  STATISTICS"
            BAR_COL  = "#C4883A"
            DIVIDER  = "─"
        else:  # cyberpunk
            BG       = "#0a0015"
            PANEL    = "#0f0020"
            ACCENT1  = "#00f5ff"   # neon cyan
            ACCENT2  = "#ff00a0"   # neon magenta
            ACCENT3  = "#b000ff"   # neon purple
            MUTED    = "#4a2060"
            TEXT     = "#cc88ff"
            GRID_COL = "#1a0035"
            TITLE    = "GAME  POINT  —  STATISTICS"
            BAR_COL  = "#00f5ff"
            DIVIDER  = "═"

        gauge_colors = [ACCENT1, ACCENT2, ACCENT3]

        fig = plt.figure(figsize=(11, 7), facecolor=BG)
        fig.subplots_adjust(left=0.07, right=0.93, top=0.88, bottom=0.1,
                            hspace=0.5, wspace=0.4)

        #Main title
        fig.text(0.5, 0.95, TITLE,
                ha="center", va="top",
                fontsize=15, fontweight="bold",
                color=ACCENT1, fontfamily="monospace")
        fig.text(0.5, 0.915, DIVIDER * 72,
                ha="center", va="top",
                fontsize=7, color=MUTED, fontfamily="monospace")

        #Gauge 1
        ax1 = fig.add_subplot(2, 3, 1)
        ax1.set_facecolor(PANEL)
        g1 = stat_store[0]
        self.draw_gauge(
            ax1, g1,
            [f"wins   {g1['win']/g1['games']*100:.1f}%",
            f"losses {g1['loss']/g1['games']*100:.1f}%",
            f"draws  {g1['draw']/g1['games']*100:.1f}%"],
            gauge_colors,
            title=self.player1,
            theme=theme,
        )

        # Gauge 2
        ax2 = fig.add_subplot(2, 3, 2)
        ax2.set_facecolor(PANEL)
        g2 = stat_store[1]
        self.draw_gauge(
            ax2, g2,
            [f"wins   {g2['win']/g2['games']*100:.1f}%",
            f"losses {g2['loss']/g2['games']*100:.1f}%",
            f"draws  {g2['draw']/g2['games']*100:.1f}%"],
            gauge_colors,
            title=self.player2,
            theme=theme,
        )

        # Game-type donut
        ax3 = fig.add_subplot(2, 3, 3)
        ax3.set_facecolor(PANEL)
        game_labels = ["TicTacToe", "Othello", "Connect 4"]
        wedges, texts, autotexts = ax3.pie(
            game_counts,
            colors=gauge_colors,
            autopct=lambda p: f"{p:.1f}%" if p > 0 else "",
            pctdistance=0.75,
            wedgeprops=dict(width=0.45, edgecolor=BG, linewidth=1.2),
            startangle=90,
        )
        for at in autotexts:
            at.set_fontsize(8)
            at.set_color(BG)
            at.set_fontweight("bold")
        ax3.legend(
            wedges, game_labels,
            loc="lower center",
            bbox_to_anchor=(0.5, -0.28),
            ncol=1, fontsize=8, frameon=False,
            labelcolor=TEXT,
        )
        ax3.set_title("Games Played", color=TEXT, fontsize=10,
                    fontfamily="monospace", pad=8)

        #Bar chart
        ax4 = fig.add_subplot(2, 1, 2)
        ax4.set_facecolor(PANEL)

        labels     = [i[0] for i in wingames][::-1]
        bar_values = [i[1] for i in wingames][::-1]

        # Highlight current two players in ACCENT2, rest in BAR_COL
        bar_colors = [
            ACCENT2 if lbl in (self.player1, self.player2) else BAR_COL
            for lbl in labels
        ]
        bars = ax4.bar(labels, bar_values, color=bar_colors,
                    width=0.45, zorder=3,
                    edgecolor=BG, linewidth=0.8)

        for bar, val in zip(bars, bar_values):
            ax4.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + max(bar_values) * 0.02,
                    str(val),
                    ha="center", va="bottom",
                    fontsize=9, color=TEXT,
                    fontfamily="monospace", fontweight="bold")

        ax4.yaxis.grid(True, color=GRID_COL, linewidth=0.8, zorder=0)
        ax4.set_axisbelow(True)
        ax4.set_xlabel("Players", color=MUTED, fontsize=10, fontfamily="monospace")
        ax4.set_ylabel("Wins",    color=MUTED, fontsize=10, fontfamily="monospace")
        ax4.set_title("Top 5 Players by Wins", color=TEXT, fontsize=11,
                    fontfamily="monospace", pad=10)
        ax4.tick_params(labelcolor=TEXT, labelsize=9)
        ax4.spines[:].set_visible(False)
        ax4.set_ylim(0, max(bar_values) * 1.18)
        ax4.spines["bottom"].set_visible(True)
        ax4.spines["bottom"].set_color(MUTED)
        ax4.spines["bottom"].set_linewidth(0.8)

        return False
    
    #the function to do on closing matplotlib
    def on_close(self, event):
        self.fig_no = -1

    def show_charts(self,style,event,theme):
        #this handles logistics to show the charts and calls draw_charts
        if self.fig_no==1 and not self.show:
            plot=pygame.transform.scale(pygame.image.load("./pictures/plot.png"),(0.8*self.width,0.85*self.height))
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 6, 18, 210))
            self.screen.blit(overlay, (0, 0))
            self.screen.blit(plot,(0.1*self.width,0.05*self.height))
            font=pygame.font.SysFont("Consolas",int(0.01*self.width),bold=True)
            self.b1.assign("MAIN MENU",0.15*self.width,0.92*self.height,0.1*self.width,0.05*self.height,font,style=style)
            self.b2.assign("QUIT",0.75*self.width,0.92*self.height,0.1*self.width,0.05*self.height,font,style=style)
            self.b1.draw(self.screen)
            self.b2.draw(self.screen)
            if self.b1.handle_event(event):
                self.chartsbut=1
                plt.close()
                self.fig_no=0
                return True
            if self.b2.handle_event(event):
                self.chartsbut=2
                plt.close()
                self.fig_no=0
                return True
        if self.fig_no == 0:
            self.draw_charts(theme)
            fig = plt.gcf()
            fig.canvas.mpl_connect('close_event', self.on_close)
            self.fig_no = 1
            if self.show:
                plt.show()
            else:
                plt.savefig("./pictures/plot.png")
        if self.fig_no == -1:
            self.fig_no = 0
            return True
        return False

    def show_intermediate(self, style, event):
        #calls fancy screen and make buttons for the final screen
        self.fancy_screen([],[],[(0.2415*self.width,0.25*self.height,0.484*self.width),
                                 (0.2415*self.width,0.5*self.height,0.484*self.width),
                                 (0.2415*self.width,0.75*self.height,0.484*self.width)],style)
        font=pygame.font.SysFont("Consolas",int(0.03*self.width),bold=True)
        self.b1.assign("MAIN MENU",0.25*self.width,0.3*self.height,0.3*self.width,0.15*self.height,font,style=style,offset=-0.05*self.width)
        self.b2.assign("QUIT",0.25*self.width,0.55*self.height,0.3*self.width,0.15*self.height,font,style=style,offset=-0.09*self.width)
        self.b1.draw(self.screen)
        self.b2.draw(self.screen)
        if self.b1.handle_event(event):
            return True
        if self.b2.handle_event(event):
            pygame.quit()
            sys.exit(0)
        return False
    def option_screen(self,width,height,pos,event,style=None):
        #the option button
        w,h=self.screen.get_size()
        self.options.assign("OPTIONS",pos[0],pos[1],width,height,pygame.font.SysFont("Consolas",int(0.1*width),bold=True),style=style)
        self.options.draw(self.screen)
        #print(self.showing_options)
        if self.options.handle_event(event) or self.showing_options:
            col=self._C_ACCENT if style==None else style[3]
            text=[(pygame.font.SysFont("Consolas",int(w*0.0319), bold=True),"GAME OPTIONS",col,0.2415*w,0.1146*h,True,0.00275*w,50)]
            bars=[(0.2415*w,0.1146*h+text[0][0].get_height()*1.2,0.484*w)]
            self.fancy_screen(text,[],bars,style)
            font=pygame.font.SysFont("Consolas",int(0.14*width),bold=True)
            self.resign1.assign("PLAYER 1 RESIGNS",int(0.2845*w),int(0.284*h),int(0.338*w),int(0.123*h),font,-int(0.05*w),style=style)
            self.resign2.assign("PLAYER 2 RESIGNS",int(0.2845*w),int(0.437*h),int(0.338*w),int(0.123*h),font,-int(0.05*w),style=style)
            self.quit.assign("QUIT GAME",int(0.2845*w),int(0.59*h),int(0.338*w),int(0.123*h),font,-int(0.08375*w),style=style)
            self.resume.assign("RESUME",int(0.2845*w),int(0.743*h),int(0.338*w),int(0.123*h),font,-int(0.09625*w),style=style)
            self.resign1.draw(self.screen)
            self.resign2.draw(self.screen)
            self.quit.draw(self.screen)
            self.resume.draw(self.screen)
            self.showing_options=True
            if self.resign1.handle_event(event):
                self.showing_options=False
                return 1
            if self.resign2.handle_event(event):
                self.showing_options=False
                return 2
            if self.quit.handle_event(event):
                self.showing_options=False
                return 3
            if self.resume.handle_event(event):
                self.showing_options=False
            return True
        return False
    def play(self):
        pass

    def win_check(self):
        pass

    def turn_change(self):
        pass


if __name__=="__main__":
    from games.tictactoe import Tictactoe
    from games.othello import Othello
    from games.connect4 import Connect4

    pygame.init()
    pygame.display.set_caption("TriGrid Engine")
    icon=pygame.transform.scale(pygame.image.load("./pictures/icon.png"),(64,64))
    pygame.display.set_icon(icon)

    #all the variables to track which step is being done and all the objects for the games and board are listed below
    width=800
    height=400
    player1=sys.argv[1]
    player2=sys.argv[2]
    board=Board(sys.argv[1],sys.argv[2],width,height)
    menu=Menu(width,height,board)
    running=True
    is_menu=True
    tic=Tictactoe(width,height,board.screen,player1,player2)
    oth=Othello(width,height,board.screen,player1,player2)
    con=Connect4(width,height,board.screen,player1,player2)
    o=3
    results=False
    stats=False
    charts=False
    intermediate=False
    fading=False
    final_result=0
    while running:
        #the main game loop
        event = pygame.event.Event(pygame.NOEVENT)
        imp=None
        for event in pygame.event.get():
            if(event.type==pygame.QUIT):
                running=False
            elif(event.type==pygame.VIDEORESIZE):
                #needed for handling window resizing
                board.width,board.height=event.w,event.h
                board.screen=pygame.display.set_mode((board.width,board.height),pygame.RESIZABLE)
                board.bg=pygame.transform.scale(board.bg,(board.width,board.height))
                if board.snapshot!=None:
                    board.snapshot=pygame.transform.scale(board.snapshot,(board.width,board.height))
                menu=Menu(board.width,board.height,board)
                tic.maximize(board.width,board.height,board.screen)
                oth.maximize(board.width,board.height,board.screen)
                con.maximize(board.width,board.height,board.screen)
                board.transition.screen = board.screen
                pygame.display.flip()
                continue
            elif event.type==pygame.KEYDOWN or event.type==pygame.MOUSEBUTTONDOWN:
                imp=event
        if imp==None:
            imp=event
        board.page()
        if is_menu:
            o=menu.draw(board.screen,imp)
            if(o!=3):
                is_menu=False
                fading=True
                if o==0:
                    board.transition.start(o,"./pictures/tictactoe.png",board)
                if o==1:
                    board.transition.start(o,"./pictures/othello.jpg",board)
                elif o==2:
                    board.transition.start(o,"./pictures/connect4.png",board)
        else:
            if fading:
                if board.transition.active():
                    board.transition.update()
                else:
                    fading=False
            elif results:
                if board.show_results(final_result,imp):
                    results=False
                    stats=True
            elif stats:
                if o==0:
                    style=None
                elif o==1:
                    style=oth.style
                elif o==2:
                    style=con.style
                if board.show_leaderboard(imp,style):
                    stats=False
                    charts=True
            elif charts:
                if o==0:
                    style=None
                    theme=2
                if o==1:
                    style=oth.style
                    theme=1
                elif o==2:
                    style=con.style
                    theme=1
                if board.show_charts(style,imp,theme):
                    charts=False
                    if board.chartsbut==0:
                        intermediate=True
                    elif board.chartsbut==1:
                        is_menu=True
                    else:
                        break
            elif intermediate:
                if o==0:
                    style=None
                elif o==1:
                    style=oth.style
                elif o==2:
                    style=con.style
                if board.show_intermediate(style,imp):
                    intermediate=False
                    is_menu=True
                    board=Board(board.player1,board.player2,width,height,None)
                    menu=Menu(width,height,board)
                    tic=Tictactoe(width,height,board.screen,player1,player2)
                    oth=Othello(width,height,board.screen,player1,player2)
                    con=Connect4(width,height,board.screen,player1,player2)
                    o=3
            else:
                if o==0:
                    obj=tic
                    stri="TicTacToe"
                elif o==1:
                    obj=oth
                    stri="Othello"
                elif o==2:
                    obj=con
                    stri="Connect 4"
                changed=obj.play(obj.turn,imp)
                if obj.p1resign:
                    winner=2
                    obj.p1resign=False
                elif obj.p2resign:
                    winner=1
                    obj.p2resign=False
                elif obj.quitted:
                    is_menu=True
                    obj.quitted=False
                else:
                    winner=obj.win_check(obj.turn)
                obj.turn_change(changed)
                if winner!="none":
                    final_result=winner
                    board.snapshot=board.screen.copy()
                    board.t0=time.time()
                    results=True
                    with open("history.csv", "a") as f:
                        today = time.strftime("%d-%m-%Y")
                        if winner==0:
                            f.write("DRAW,"+board.player1+","+board.player2+","+"NA,NA,"+str(today)+","+stri+"\n")
                        elif winner==1:
                            f.write("NOT DRAW,"+board.player1+","+board.player2+","+board.player1+","+board.player2+","+str(today)+","+stri+"\n")
                        else:
                            f.write("NOT DRAW,"+board.player1+","+board.player2+","+board.player2+","+board.player1+","+str(today)+","+stri+"\n")
        pygame.display.flip()
    pygame.quit()
