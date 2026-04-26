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
    def __init__(self, text, x, y, w, h, font):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = font
        self.hovered = False
        self.pulse_t = 0.0
        self._last_draw_time = None
        self.accent = (0,200,255)
        self.bg     = (0,13,26)
        self.dim    = (26,96,144)

    def assign(self, text, x, y, w, h, font):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = font

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
        screen.blit(txt,(x+(w-txt.get_width())//2,y+(h-txt.get_height())//2))


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

    def draw(self, screen):
        r   = self.radius
        box = pygame.Rect(self.x - r, self.y - r, r * 2, r * 2)
        glow_alpha = 180 if self.selected else 60
        for spread in (r + 6, r + 4, r + 2):
            glow_surf = pygame.Surface((spread * 2, spread * 2), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (0, 160, 255, glow_alpha // (spread - r + 1)),
                             (0, 0, spread * 2, spread * 2), border_radius=4)
            screen.blit(glow_surf, (self.x - spread, self.y - spread))
        if self.selected:
            pygame.draw.rect(screen, (0, 60, 120), box, border_radius=3)
        else:
            pygame.draw.rect(screen, (2, 15, 35), box, border_radius=3)

        pygame.draw.rect(screen, (0, 140, 220), box, 1, border_radius=3)
        if self.selected:
            badge_font = self.font_box
            num = badge_font.render(str(self.priority), True, (0, 220, 255))
            screen.blit(num, (box.center[0] - num.get_width()//2, box.center[1]-num.get_height()//2))
        text_col = (180, 220, 255) if self.selected else (60, 110, 160)
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
                pygame.draw.circle(gs, (0, 200, 255, 40), (spread, spread), spread)
                screen.blit(gs, (rx - spread, ry - spread))

        pygame.draw.circle(screen, (0, 80, 140), (rx, ry), radio_r)
        pygame.draw.circle(screen, (0, 140, 220), (rx, ry), radio_r, 1)

        if self.reverse:
            pygame.draw.circle(screen, (0, 200, 255), (rx, ry), radio_r // 2)

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
    _C_BG       = (2,   10,  24)   # deep navy fill
    _C_PANEL    = (4,   18,  40)   # panel surface
    _C_GRID     = (8,   22,  48)   # grid line colour
    _C_BORDER   = (0,  100, 200)   # accent border
    _C_ACCENT   = (0,  180, 255)   # bright cyan-blue
    _C_DIM      = (0,   60, 120)   # dim accent
    _C_TEXT     = (160, 210, 255)  # primary text
    _C_MUTED    = (50,  100, 150)  # muted text / section labels
    _C_GLOW     = (0,  140, 220)   # glow tint

    def __init__(self,player1,player2,width,height,stats):
        self.player1=player1
        self.player2=player2
        self.screen=pygame.display.set_mode((width,height),pygame.RESIZABLE)
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

    def draw_hbar(self, surf, x, y, w, glow_alpha=60):
        """Horizontal rule with a short bright left cap."""
        color = (0,  180, 255)
        dim   = (0,   60, 120)
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

    def show_leaderboard(self, event):
        """
        Sci-fi redesign of the leaderboard sort-options page.
        All original logic (checkbox select/deselect, priority tracking,
        reverse radio, Generate + Visualize buttons) is unchanged.
        """
        w, h = self.width, self.height
        pw = int(w * 0.55)
        ph = int(h * 0.82)
        px = (w - pw) // 2
        py = (h - ph) // 2
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 6, 18, 210))
        self.screen.blit(overlay, (0, 0))
        panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
        panel.fill((*self._C_PANEL, 245))
        self.screen.blit(panel, (px, py))
        glow_s = pygame.Surface((pw, ph), pygame.SRCALPHA)
        for radius in range(int(120/400*self.height), 0, int(-20/400*self.height)):
            alpha = max(0, 18 - (120 - radius*400/self.height) // 6)
            pygame.draw.circle(glow_s, (0,180,255, alpha),
                               (pw - 40*400/self.height, 40*400/self.height), radius)
        self.screen.blit(glow_s, (px, py))
        pygame.draw.rect(self.screen, self._C_BORDER,
                         (px, py, pw, ph), 1, border_radius=4)
        self.draw_corner_brackets(self.screen, px, py, pw, ph,
                                   arm=16, color=(0,180,255), alpha=200)
        title_font = pygame.font.SysFont("Consolas",int(pw * 0.058), bold=True)
        title_x = px + int(pw * 0.03)
        title_y = py + int(ph * 0.03)
        self.glow_text(self.screen, title_font,"Sort Mode of Leaderboard",(0,180,255), title_x, title_y,spread=int(pw*0.005), glow_alpha=50)
        self.draw_hbar(self.screen,title_x, title_y + title_font.get_height()*1.2,pw - int(pw * 0.12))
        sec_font = pygame.font.SysFont("Consolas", int(pw * 0.028))
        sec_surf = sec_font.render("SELECT  &  PRIORITISE  COLUMNS",True, (0,180,255))
        self.screen.blit(sec_surf,(title_x,py+ph*0.2))
        rev_font  = pygame.font.SysFont("Consolas", int(pw * 0.030))
        rev_label = rev_font.render("REVERSE", True, (0,180,255))
        rev_x     = px + int(pw * 0.94)
        rev_y     = py + int(ph * 0.2)
        self.screen.blit(rev_label, (rev_x - rev_label.get_width(), rev_y))
        cx      = px + int(pw * 0.10)
        row_y   = [
            py + int(ph * 0.279),
            py + int(ph * 0.358),
            py + int(ph * 0.437),
            py + int(ph * 0.516),
            py + int(ph * 0.595),
            py + int(ph * 0.674),
            py + int(ph * 0.753),
        ]
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

        for i, obj in enumerate(objs):
            obj.assign(cx, row_y[i], pw, labels[i])
            if obj.selected:
                stripe = pygame.Surface((obj.radius*2.1,obj.radius*2.1),
                                        pygame.SRCALPHA)
                stripe.fill((0, 100, 200, 18))
                self.screen.blit(stripe,(cx-obj.radius*1.05,row_y[i] - obj.radius*1.05))
            obj.draw(self.screen)

        div_y = py + int(ph * 0.802)
        self.draw_hbar(self.screen, px + int(pw * 0.04), div_y,pw - int(pw * 0.08))

        btn_font = pygame.font.SysFont("Consolas", int(pw * 0.040), bold=True)
        self.ldb_but.assign("Generate",
                            px + int(pw * 0.66),
                            py + int(ph * 0.842),
                            int(pw * 0.3),
                            int(ph * 0.12),
                            btn_font)
        self.charts.assign("Visualize",
                           px + int(pw * 0.04),
                           py + int(ph * 0.842),
                           int(pw * 0.3),
                           int(ph * 0.12),
                           btn_font)
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

    def draw_gauge(self, ax, values, texts, color):
        gap       = 90
        total_arc = 360 - gap
        start_angle = 90 + gap / 2
        filled_frac = [
            values["win"]  / values["games"],
            values["loss"] / values["games"],
            values["draw"] / values["games"],
        ]
        filled_deg = list(total_arc * np.array(filled_frac)/360)
        ring_width = 0.22
        ax.pie(
            filled_deg + [gap/360],
            startangle=start_angle,
            colors=color + ["none"],
            wedgeprops=dict(width=ring_width, edgecolor="none"),
            counterclock=False,
        )
        for i in range(len(texts)):
            ax.text(0,-0.3*(i-(len(texts)-1)/2),texts[i],ha="center",va="center",fontsize=10,fontweight="bold",color="white")
        ax.axis("off")

    def draw_charts(self):
        stat_store=[{"games":0,"win":0,"loss":0,"draw":0},{"games":0,"win":0,"loss":0,"draw":0}]
        win_players={}
        game_counts=[0,0,0]
        with open("history.csv","r") as f:
            for line in f:
                arr=line.split(",")
                arr[6]=arr[6].removesuffix("\n")
                if arr[1]==self.player1 or arr[2]==self.player1:
                    stat_store[0]["games"]+=1
                    if arr[0]=="DRAW":
                        stat_store[0]["draw"]+=1
                    else:
                        if arr[3]==self.player1:
                            stat_store[0]["win"]+=1
                        else:
                            stat_store[0]["loss"]+=1
                if arr[1]==self.player2 or arr[2]==self.player2:
                    stat_store[1]["games"]+=1
                    if arr[0]=="DRAW":
                        stat_store[1]["draw"]+=1
                    else:
                        if arr[3]==self.player2:
                            stat_store[1]["win"]+=1
                        else:
                            stat_store[1]["loss"]+=1
                if arr[3] in win_players.keys():
                    win_players[arr[3]]+=1
                elif arr[3]!="NA":
                    win_players[arr[3]]=1
                if arr[6]=="TicTacToe":
                    game_counts[0]+=1
                elif arr[6]=="Othello":
                    game_counts[1]+=1
                else:
                    game_counts[2]+=1
        wingames=sorted(win_players.items(),key=lambda x:x[1],reverse=True)[:5]
        fig, axes = plt.subplots(2,2)
        fig.patch.set_facecolor("#0d1b2a")
        colors = ["#00cfcf", "#f97316","#1F7716"]
        games1 = stat_store[0]["games"]
        games2 = stat_store[1]["games"]
        self.draw_gauge(axes[0][0],stat_store[0],
                        [f'wins:{stat_store[0]["win"]/games1*100:.2f}',
                         f'loss:{stat_store[0]["loss"]/games1*100:.2f}',
                         f'draws:{stat_store[0]["draw"]/games1*100:.2f}'],
                        colors)
        self.draw_gauge(axes[0][1],stat_store[1],
                        [f'wins:{stat_store[1]["win"]/games2*100:.2f}',
                         f'loss:{stat_store[1]["loss"]/games2*100:.2f}',
                         f'draws:{stat_store[1]["draw"]/games2*100:.2f}'],
                        colors)
        labels = [i[0] for i in wingames][::-1]
        values = [i[1] for i in wingames][::-1]
        axes[1][0].bar(labels, values, color="#B74005", width=0.4)
        axes[1][0].set_facecolor("#0d1b2a")
        axes[1][0].set_xlabel("Players", color="white", fontsize=10)
        axes[1][0].set_ylabel("Wins",    color="white", fontsize=10)
        axes[1][0].set_title("Top 5 Players by Wins", color="white", fontsize=11)
        axes[1][0].tick_params(labelcolor="white")
        for spine in axes[1][0].spines.values():
            spine.set_visible(False)
        wedges=axes[1][1].pie(game_counts,colors=["#4fc3f7", "#ce93d8", "#80cbc4"],autopct=lambda pct: f'{pct:.1f}%' if pct > 0 else '')[0]
        axes[1][1].legend(
            wedges,
            ["tictactoe", "othello", "connect4"],
            loc="center left",
            bbox_to_anchor=(1, 0.5),
            fontsize=8
        )
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
    oth=Othello(width,height,board.screen)
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
                if board.show_leaderboard(imp):
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
                    oth=Othello(width,height,board.screen)
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