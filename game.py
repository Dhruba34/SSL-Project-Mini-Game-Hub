import pygame
import numpy as np
import time
import os
import sys
import matplotlib.pyplot as plt
import math

class TransitionManager:
    GAME_NAMES  = {0: "TIC TAC TOE", 1: "OTHELLO", 2: "CONNECT 4"}
    GAME_COLORS = {
        0: (0, 200, 255),
        1: (180, 100, 255),
        2: (255, 140, 0),
    }

    def __init__(self, screen):
        self.screen=screen
        self.state="idle"
        self.t0=0.0
        self.game= 0
        self.snapshot=None
        self.just_finished=False
        self.fade_duration=0.5
        self.show_duration=3.6
        self.reveal_duration=1.5
        self.reveal_img=""
        self.board=None

    def start(self, game_index,reveal_img,board):
        self.game=game_index
        self.t0=time.time()
        self.state="fade_out"
        self.snapshot=self.screen.copy()
        self.reveal_img=reveal_img
        self.board=board

    def active(self):
        return self.state!="idle"

    @property
    def done(self) -> bool:
        return self.state=="idle" and self.just_finished

    def update(self):
        self.just_finished = False
        if self.state=="idle":
            return
        now=time.time()
        elapsed=now-self.t0
        w,h=self.screen.get_size()

        if self.state=="fade_out":
            alpha=int(255*min(elapsed/self.fade_duration,1.0))
            if self.snapshot:
                snap=pygame.transform.scale(self.snapshot,(w,h))
                self.screen.blit(snap,(0,0))
            overlay = pygame.Surface((w,h))
            overlay.fill((0,0,0))
            overlay.set_alpha(alpha)
            self.screen.blit(overlay, (0,0))
            if elapsed>=self.fade_duration:
                self.t0=now
                self.state="show"
        elif self.state=="show":
            self.draw_splash(w, h, elapsed)
            if elapsed >= self.reveal_duration + self.show_duration:
                self.t0=now
                self.state="fade_in"
                self.snapshot=pygame.image.load(self.reveal_img)
                self.board.bg=pygame.transform.scale(pygame.image.load(self.reveal_img),(self.board.width,self.board.height))
        elif self.state=="fade_in":
            alpha=int(255*(1-min(elapsed/self.fade_duration,1)))
            overlay=pygame.Surface((w, h))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(alpha)
            self.screen.blit(overlay, (0, 0))
            if elapsed>=self.fade_duration:
                self.state="idle"
                self.just_finished=True

    def draw_splash(self, w, h, elapsed):
        accent=self.GAME_COLORS[self.game]
        name=self.GAME_NAMES[self.game]
        self.screen.fill((0, 0, 0))
        for y in range(0, h, 18):
            pygame.draw.line(self.screen, (10, 10, 10), (0, y), (w, y),1)
        for x in range(0, w, 36):
            pygame.draw.line(self.screen, (8, 8, 8), (x, 0), (x, h), 1)
        t_pulse = elapsed*3.0
        bar_alpha = int(80 + 60 * math.sin(t_pulse))
        bar_surf = pygame.Surface((w, 3), pygame.SRCALPHA)
        bar_surf.fill((*accent, bar_alpha))
        self.screen.blit(bar_surf, (0, h // 2 - 60))
        self.screen.blit(bar_surf, (0, h // 2 + 60))
        margin, arm = 24, 22
        bk_alpha = min(255, int(255 * elapsed / 0.2))
        bk_surf  = pygame.Surface((w, h), pygame.SRCALPHA)
        c = (*accent, bk_alpha)
        pairs = [
            ((margin, margin),         (1, 0), (0, 1)),
            ((w - margin, margin),     (-1, 0), (0, 1)),
            ((margin, h - margin),     (1, 0), (0, -1)),
            ((w - margin, h - margin), (-1, 0), (0, -1)),
        ]
        for (cx, cy), (dx, dy), (ex, ey) in pairs:
            pygame.draw.line(bk_surf, c, (cx, cy), (cx + dx*arm, cy + dy*arm), 2)
            pygame.draw.line(bk_surf, c, (cx, cy), (cx + ex*arm, cy + ey*arm), 2)
        self.screen.blit(bk_surf, (0, 0))
        reveal_frac = min(elapsed/self.reveal_duration, 1.0)
        chars_shown  = int(len(name) * reveal_frac)
        visible_text = name[:chars_shown]
        cursor       = "_" if chars_shown < len(name) else ""
        font_size = max(28, min(72, int(w * 0.075)))
        try:
            font = pygame.font.SysFont("Consolas", font_size, bold=True)
        except Exception:
            font = pygame.font.Font(None, font_size)
        glow_surf = font.render(visible_text + cursor, True,
                                tuple(max(0, c - 100) for c in accent))
        gx = (w - glow_surf.get_width())  // 2
        gy = (h - glow_surf.get_height()) // 2
        for off in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            self.screen.blit(glow_surf, (gx + off[0], gy + off[1]))
        txt = font.render(visible_text + cursor, True, accent)
        self.screen.blit(txt, (gx, gy))
        if reveal_frac >= 1.0:
            sub_alpha = int(255 * min((elapsed-self.reveal_duration) / 0.3, 1.0))
            sub_font  = pygame.font.SysFont("Consolas", max(12, font_size // 4))
            sub       = sub_font.render("LOADING BOARD...", True, accent)
            sub_surf  = pygame.Surface((sub.get_width(), sub.get_height()), pygame.SRCALPHA)
            sub_surf.blit(sub, (0, 0))
            sub_surf.set_alpha(sub_alpha)
            self.screen.blit(sub_surf,
                             ((w - sub.get_width()) // 2,
                              gy + glow_surf.get_height() + 18))


class Button:
    def __init__(self, text, x, y, w, h, font,offset=0,style=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = font
        self.hovered = False
        self.pulse_t = 0.0
        self._last_draw_time = None
        if style==None:
            self.accent = (0,200,255)
            self.bg     = (0,13,26)
            self.dim    = (26,96,144)
        else:
            self.accent,self.bg,self.dim=style[0],style[1],style[2]
        self.offset=offset

    def assign(self, text, x, y, w, h, font,offset=0,style=None):
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

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    def polygon(self, notch=12):
        x, y, w, h = self.rect
        notch=int(12/45*h)
        return [
            (x + notch, y),
            (x + w,     y),
            (x + w,     y + h),
            (x,         y + h),
            (x,         y + notch),
        ]

    def draw(self,screen):
        x,y,w,h=self.rect
        notch=int(12/45*h)
        accent=self.accent
        dim=self.dim
        poly=self.polygon(notch)
        local_poly=[(px-x,py-y) for px,py in poly]
        bg_surf=pygame.Surface((w,h),pygame.SRCALPHA)
        pygame.draw.polygon(bg_surf,(*self.bg,230),local_poly)
        screen.blit(bg_surf,(x,y))
        pulse=0.55+0.45*math.sin(self.pulse_t)
        border_color=tuple(int(c*pulse) for c in dim) if not self.hovered else accent
        border_alpha=255 if self.hovered else int(180*pulse)
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
        text_color=(255,255,255) if self.hovered else accent
        txt=self.font.render(self.text,True,text_color)
        screen.blit(txt,(x+(w-txt.get_width())//2+self.offset,y+(h-txt.get_height())//2))


class Checkbox:
    def __init__(self, x, y, rect_width,text,idx,font_name="Consolas", font_size=22,
                 text_color=(255,255,255), selected_color=(70, 130, 180),
                 unselected_color=(100, 100, 100), radius=10):
        self.x = x
        self.y = y
        self.displaywidth=rect_width
        self.text = text
        font_size=int(9/320*rect_width)
        self.font = pygame.font.SysFont(font_name, font_size)
        self.font_box=pygame.font.SysFont(font_name,18)
        self.text_color = text_color
        self.selected_color = selected_color
        self.unselected_color = unselected_color
        self.radius = radius
        self.selected = False
        self.idx=idx
        self.reverse=False
        self.rect=None
        self.priority=0
        self.radiorect=None

    def assign(self,x,y,rect_width,text,font_name="Consolas",font_size=22,text_color=(255,255,255),selected_color=(70,130,180),
               unselected_color=(100,100,100)):
        self.x = x
        self.y = y
        self.displaywidth=rect_width
        self.text = text
        font_size=int(12/320*rect_width)
        self.font = pygame.font.SysFont(font_name, font_size)
        self.font_box=pygame.font.SysFont(font_name,int(0.75*font_size))
        self.text_color = text_color
        self.selected_color = selected_color
        self.unselected_color = unselected_color
        self.radius = self.font.render("a",True,(0,0,0)).get_height()//2

    def select(self):
        self.selected = True

    def deselect(self):
        self.selected = False

    def draw(self, screen,style=None):
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
        col=(180,220,255) if style==None else (220,255,180)
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


class Menu:
    def __init__(self,width,height,board):
        self.width=width
        self.height=height
        self.baord=board
        self.font=pygame.font.SysFont("Consolas",int(min(18/800*width,18/400*height)))
        self.font2=pygame.font.SysFont("Consolas",int(min(30/800*width,30/400*height)))
        self.tictactoe=Button("TicTacToe",0.4*width,0.35*height,0.2*width,0.1125*height,self.font)
        self.othello=Button("Othello",0.4*width,0.51875*height,0.2*width,0.1125*height,self.font)
        self.connect4=Button("Connect4",0.4*width,0.6875*height,0.2*width,0.1125*height,self.font)

    def draw(self,screen,event):
        board.bg=pygame.transform.scale(pygame.image.load("./pictures/background4.png"),(self.width,self.height))
        self.tictactoe.draw(screen)
        self.othello.draw(screen)
        self.connect4.draw(screen)
        title=self.font2.render("SELECT GAME",True,(235, 205, 205))
        screen.blit(title,pygame.Rect(0.38125*self.width,0.2*self.height,0.3*self.width,0.1*self.height))
        if self.tictactoe.handle_event(event):
            return 0
        elif self.othello.handle_event(event):
            return 1
        elif self.connect4.handle_event(event):
            return 2
        else:
            return 3


class Board:
    _C_PANEL    = (4,   18,  40)   # panel surface
    _C_BORDER   = (0,  100, 200)   # accent border
    _C_ACCENT   = (0,  180, 255)   # bright cyan-blue

    def __init__(self,player1,player2,width,height,stats,screen=None):
        self.player1=player1
        self.player2=player2
        if screen==None:
            self.screen=pygame.display.set_mode((width,height),pygame.RESIZABLE)
        else:
            self.screen=screen
        self.stats=stats
        self.width=width
        self.height=height
        self.bg=pygame.image.load("./pictures/background2.png")
        self.bg=pygame.transform.scale(self.bg,(self.width,self.height))
        self.leaderboard=Button("",0,0,0,0,None)
        self.board=None
        self.o1=Checkbox(0,0,0,"",1)
        self.o2=Checkbox(0,0,0,"",2)
        self.o3=Checkbox(0,0,0,"",3)
        self.o4=Checkbox(0,0,0,"",4)
        self.o5=Checkbox(0,0,0,"",5)
        self.o6=Checkbox(0,0,0,"",6)
        self.o7=Checkbox(0,0,0,"",7)
        self.default=[1,2,3,4,5,6,7]
        self.ldb_but=Button("",0,0,0,0,None)
        self.charts=Button("",0,0,0,0,None)
        self.fig_no=0
        self.b1=Button("",0,0,0,0,None)
        self.b2=Button("",0,0,0,0,None)
        self.priorities=[]
        self.transition = TransitionManager(self.screen)
        self.t0=None
        self.snapshot=None
        self.resign1=None
        self.resign2=None
        self.quit=None
        self.options=Button("",0,0,0,0,None)
        self.resign1=Button("",0,0,0,0,None)
        self.resign2=Button("",0,0,0,0,None)
        self.quit=Button("",0,0,0,0,None)
        self.resume=Button("",0,0,0,0,None)
        self.showing_options=False

    def draw_corner_brackets(self, surf, rx, ry, rw, rh, arm=18, color=None, alpha=255, thick=2):
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

    def draw_hbar(self, surf, x, y, w, glow_alpha=60,accent=_C_ACCENT,border=_C_BORDER):
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

    def glow_text(self, surf, font, text, color, x, y, spread=3, glow_alpha=40):
        """Blit text with a soft outer glow."""
        glow_col = tuple(min(255, int(c * 0.6)) for c in color)
        glow_s   = font.render(text, True, glow_col)
        glow_s.set_alpha(glow_alpha)
        for ox, oy in [(-spread,0),(spread,0),(0,-spread),(0,spread)]:
            surf.blit(glow_s, (x + ox, y + oy))
        main = font.render(text,True, color)
        surf.blit(main, (x, y))

    def page(self):
        self.screen.blit(self.bg,(0,0))
    def show_leaderboard(self,event,style=None):
        w,h=self.width,self.height
        if style==None:
            accent=(0,180,255)
        else:
            accent=style[3]
        title=(pygame.font.SysFont("Consolas",int(w*0.0319), bold=True),"Sort Mode of Leaderboard",accent,0.2415*w,0.1146*h,True,0.00275*w,50)
        sec_font=pygame.font.SysFont("Consolas", int(w*0.0154))

        select=(sec_font,"SELECT  &  PRIORITISE  COLUMNS",accent,0.2415*w,0.254*h,False)
        txt=sec_font.render("REVERSE",True,(0,0,0))
        rev=(sec_font,"REVERSE",accent,0.742*w-txt.get_width(),0.254*h,False)
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
        self.ldb_but.assign("Generate",0.588*w,0.78044*h,0.165*w,0.0984*h,pygame.font.SysFont("Consolas", int(0.022*w), bold=True),style=style)
        self.charts.assign("Visualize",0.247*w,0.7804*h,0.165*w,0.0984*h,pygame.font.SysFont("Consolas", int(0.022*w), bold=True),style=style)
        bars=[(0.2415*w,0.1146*h+title[0].get_height()*1.2,0.484*w),(0.247*w,0.74764*h,0.506*w)]
        self.fancy_screen([title,select,rev],checks,bars,style)
        self.ldb_but.draw(self.screen)
        self.charts.draw(self.screen)

        rects      = [o.rect      for o in objs]
        radiorects = [o.radiorect for o in objs]

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
            return True
        if self.ldb_but.handle_event(event):
            preference = [-o.idx if o.reverse else o.idx for o in self.priorities]
            arr=self.default
            for i in preference: arr.remove(abs(i))
            preference=preference+arr 
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
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 6, 18, 210))
        self.screen.blit(overlay, (0, 0))
        panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
        panel.fill((*panelc, 245))
        self.screen.blit(panel, (px, py))
        glow_s = pygame.Surface((pw, ph), pygame.SRCALPHA)
        for radius in range(int(120/400*self.height), 0, int(-20/400*self.height)):
            alpha = max(0, 18 - (120 - radius*400/self.height) // 6)
            pygame.draw.circle(glow_s, (*accentc, alpha),(pw - 40*400/self.height, 40*400/self.height), radius)
        self.screen.blit(glow_s, (px, py))
        pygame.draw.rect(self.screen, borderc,
                         (px, py, pw, ph), 1, border_radius=4)
        self.draw_corner_brackets(self.screen, px, py, pw, ph,
                                   arm=16, color=borderc, alpha=200)
        
        for i in texts:
            if i[5]:
                self.glow_text(self.screen,*i[:5],spread=i[6],glow_alpha=i[7])
            else:
                self.glow_text(self.screen,*i[:-1])
        

        for i in checks:
            obj=i[3]
            obj.assign(i[0], i[1], pw, i[2])
            if obj.selected:
                stripe = pygame.Surface((obj.radius*2.1,obj.radius*2.1),
                                        pygame.SRCALPHA)
                stripe.fill((*borderc, 18))
                self.screen.blit(stripe,(i[0]-obj.radius*1.05,i[1] - obj.radius*1.05))
            obj.draw(self.screen,style)

        for bar in bars:
            if style==None:
                self.draw_hbar(self.screen,*bar)
            else:
                self.draw_hbar(self.screen,*bar,accent=style[3],border=style[4])
        

    def draw_results(self, text, color=(171, 64, 2)):
        w, h = self.screen.get_size()
        elapsed = time.time() - self.t0
        self.screen.blit(self.snapshot, (0, 0))
        fade = min(1, elapsed / 0.6)
        fade = fade * fade
        dark_alpha = int(200 * fade)
        bar_alpha  = int(180 * fade)
        dark = pygame.Surface((w, h), pygame.SRCALPHA)
        dark.fill((0, 0, 0, dark_alpha))
        self.screen.blit(dark, (0, 0))
        bar_height = int(0.20 * h)
        bar_y = h // 2 - bar_height // 2
        for i in range(bar_height):
            t = abs(i - bar_height / 2) / (bar_height / 2)
            alpha = int(bar_alpha * (1 - t * t))
            line = pygame.Surface((w, 1), pygame.SRCALPHA)
            line.fill((0, 0, 0, alpha))
            self.screen.blit(line, (0, bar_y + i))
        def glow_line(y):
            for i in range(10, 0, -1):
                surf = pygame.Surface((w, 2), pygame.SRCALPHA)
                surf.fill((*color, 18 * i))
                self.screen.blit(surf, (0, y - i))
        glow_line(bar_y)
        glow_line(bar_y + bar_height)
        font_size = int(h * 0.09)
        font = pygame.font.SysFont("Georgia", font_size, bold=True)
        txt  = font.render(text, True, color)
        while txt.get_width() > w * 0.85 and font_size > 20:
            font_size -= 2
            font = pygame.font.SysFont("Georgia", font_size, bold=True)
            txt  = font.render(text, True, color)
        tx = w // 2 - txt.get_width() // 2
        ty = h // 2 - txt.get_height() // 2
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
        sub = font_small.render("Press SPACE to continue", True, (200, 200, 200))
        sub.set_alpha(alpha)
        sx = w // 2 - sub.get_width() // 2
        sy = bar_height * 1.1 + bar_y
        self.screen.blit(sub, (sx, sy))

    def show_results(self, winner, event):
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

    def draw_gauge(self, ax, values, texts, colors, title=""):
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
            wedgeprops=dict(width=ring_width, edgecolor="#1a0f08", linewidth=1.5),
            counterclock=False,
        )
        # Subtle inner ring shadow
        ax.add_patch(plt.Circle((0, 0), 1 - ring_width - 0.04,
                                color="#12080300", zorder=0))

        label_colors = ["#E8A44A", "#C0523A", "#6B9E7A"]
        icons        = ["▲", "▼", "—"]
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
                    color="#D4A868", fontfamily="monospace")
        ax.axis("off")


    def draw_charts(self):
        stat_store = [
            {"games": 0, "win": 0, "loss": 0, "draw": 0},
            {"games": 0, "win": 0, "loss": 0, "draw": 0},
        ]
        win_players = {}
        game_counts = [0, 0, 0]

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

        BG       = "#1a0f08"
        PANEL    = "#1e1208"
        COPPER   = "#E8A44A"
        RUST     = "#C0523A"
        TEAL     = "#6B9E7A"
        MUTED    = "#8B6040"
        TEXT     = "#D4A868"
        GRID_COL = "#2a1c0e"

        gauge_colors = [COPPER, RUST, TEAL]

        fig = plt.figure(figsize=(11, 7), facecolor=BG)
        fig.subplots_adjust(left=0.07, right=0.93, top=0.88, bottom=0.1,
                            hspace=0.5, wspace=0.4)

        # ── Main title ──────────────────────────────────────────────
        fig.text(0.5, 0.95, "GAME  POINT  —  STATISTICS",
                ha="center", va="top",
                fontsize=15, fontweight="bold",
                color=COPPER, fontfamily="monospace"
                )
        fig.text(0.5, 0.915, "─" * 72,
                ha="center", va="top",
                fontsize=7, color=MUTED, fontfamily="monospace")

        # ── Gauge 1 ──────────────────────────────────────────────────
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
        )

        # ── Gauge 2 ──────────────────────────────────────────────────
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
        )

        # ── Game-type donut (top-right) ───────────────────────────────
        ax3 = fig.add_subplot(2, 3, 3)
        ax3.set_facecolor(PANEL)
        donut_colors = [COPPER, RUST, TEAL]
        game_labels  = ["TicTacToe", "Othello", "Connect 4"]
        wedges, texts, autotexts = ax3.pie(
            game_counts,
            colors=donut_colors,
            autopct=lambda p: f"{p:.1f}%" if p > 0 else "",
            pctdistance=0.75,
            wedgeprops=dict(width=0.45, edgecolor="#1a0f08", linewidth=1.2),
            startangle=90,
        )
        for at in autotexts:
            at.set_fontsize(8)
            at.set_color("#1a0f08")
            at.set_fontweight("bold")
        ax3.legend(
            wedges, game_labels,
            loc="lower center",
            bbox_to_anchor=(0.5, -0.28),
            ncol=1,
            fontsize=8,
            frameon=False,
            labelcolor=TEXT,
        )
        ax3.set_title("Games Played", color=TEXT, fontsize=10,
                    fontfamily="monospace", pad=8)

        # ── Bar chart (bottom, full width) ───────────────────────────
        ax4 = fig.add_subplot(2, 1, 2)
        ax4.set_facecolor(PANEL)

        labels = [i[0] for i in wingames][::-1]
        bar_values = [i[1] for i in wingames][::-1]

        bar_colors = [COPPER, "#C4883A", RUST, "#9B3A28", TEAL][:len(labels)]
        bars = ax4.bar(labels, bar_values, color=bar_colors,
                    width=0.45, zorder=3,
                    edgecolor="#1a0f08", linewidth=0.8)

        # Value labels on top of bars
        for bar, val in zip(bars, bar_values):
            ax4.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + max(bar_values) * 0.02,
                    str(val),
                    ha="center", va="bottom",
                    fontsize=9, color=TEXT,
                    fontfamily="monospace", fontweight="bold")

        # Horizontal grid lines only
        ax4.yaxis.grid(True, color=GRID_COL, linewidth=0.8, zorder=0)
        ax4.set_axisbelow(True)
        ax4.set_facecolor(PANEL)
        ax4.set_xlabel("Players", color=MUTED, fontsize=10, fontfamily="monospace")
        ax4.set_ylabel("Wins",    color=MUTED, fontsize=10, fontfamily="monospace")
        ax4.set_title("Top 5 Players by Wins",
                    color=TEXT, fontsize=11,
                    fontfamily="monospace", pad=10)
        ax4.tick_params(labelcolor=TEXT, labelsize=9)
        ax4.spines[:].set_visible(False)
        ax4.set_ylim(0, max(bar_values) * 1.18)

        # Thin copper bottom border
        ax4.spines["bottom"].set_visible(True)
        ax4.spines["bottom"].set_color(MUTED)
        ax4.spines["bottom"].set_linewidth(0.8)

        return False

    def on_close(self, event):
        self.fig_no = -1

    def show_charts(self):
        if self.fig_no == 0:
            self.draw_charts()
            fig = plt.gcf()
            fig.canvas.mpl_connect('close_event', self.on_close)
            self.fig_no = 1
            plt.show()
        if self.fig_no == -1:
            self.fig_no = 0
            return True
        return False

    def show_intermediate(self, obj, event):
        winw=obj.playing_board.width
        winh=obj.playing_board.height
        rect=pygame.Rect((self.width-winw)/2,(self.height-winh)/2,winw,winh)
        pygame.draw.rect(self.screen,(0,0,0),rect,border_radius=10)
        font=pygame.font.SysFont("Consolas",int(12*winw/120),bold=True)
        self.b1.assign("Main Menu",int(self.width//2-0.35*winw),int(self.height//2-0.35*winh),int(0.7*winw),int(0.25*winh),font)
        self.b2.assign("Quit",int(self.width//2-0.35*winw),int(self.height//2+0.1*winh),int(0.7*winw),int(0.25*winh),font)
        self.b1.draw(self.screen)
        self.b2.draw(self.screen)
        if self.b1.handle_event(event):
            return True
        if self.b2.handle_event(event):
            pygame.quit()
            sys.exit()
        return False
    def option_screen(self,width,height,pos,event,style=None):
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
    pygame.display.set_caption("Game Point")
    icon=pygame.transform.scale(pygame.image.load("./pictures/icon.png"),(64,64))
    pygame.display.set_icon(icon)

    width=800
    height=400
    player1=sys.argv[1]
    player2=sys.argv[2]
    board=Board(sys.argv[1],sys.argv[2],width,height,None)
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
        event = pygame.event.Event(pygame.NOEVENT)
        imp=None
        for event in pygame.event.get():
            if(event.type==pygame.QUIT):
                running=False
            elif(event.type==pygame.VIDEORESIZE):
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
                elif o==1:
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
                elif o==2:
                    style=con.style
                if board.show_leaderboard(imp,style):
                    stats=False
                    charts=True
            elif charts:
                if board.show_charts():
                    charts=False
                    intermediate=True
            elif intermediate:
                if o==0:
                    obj=tic
                elif o==1:
                    obj=oth
                elif o==2:
                    obj=con
                if board.show_intermediate(obj,imp):
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
