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
        """True for exactly one frame after FADE_IN finishes."""
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

        # --- solid black background ---
        self.screen.fill((0, 0, 0))

        # --- scanline grid (subtle) ---
        for y in range(0, h, 18):
            pygame.draw.line(self.screen, (10, 10, 10), (0, y), (w, y),1)
        for x in range(0, w, 36):
            pygame.draw.line(self.screen, (8, 8, 8), (x, 0), (x, h), 1)

        # --- horizontal accent bars ---
        t_pulse = elapsed*3.0
        bar_alpha = int(80 + 60 * math.sin(t_pulse))
        bar_surf = pygame.Surface((w, 3), pygame.SRCALPHA)
        bar_surf.fill((*accent, bar_alpha))
        self.screen.blit(bar_surf, (0, h // 2 - 60))
        self.screen.blit(bar_surf, (0, h // 2 + 60))

        # --- corner brackets ---
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

        # --- reveal progress (character scan effect) ---
        reveal_frac = min(elapsed/self.reveal_duration, 1.0)
        chars_shown  = int(len(name) * reveal_frac)
        visible_text = name[:chars_shown]
        cursor       = "_" if chars_shown < len(name) else ""

        font_size = max(28, min(72, int(w * 0.075)))
        try:
            font = pygame.font.SysFont("Consolas", font_size, bold=True)
        except Exception:
            font = pygame.font.Font(None, font_size)

        # glow pass (slightly larger, dimmer, same colour)
        glow_surf = font.render(visible_text + cursor, True,
                                tuple(max(0, c - 100) for c in accent))
        gx = (w - glow_surf.get_width())  // 2
        gy = (h - glow_surf.get_height()) // 2
        for off in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            self.screen.blit(glow_surf, (gx + off[0], gy + off[1]))

        # main text
        txt = font.render(visible_text + cursor, True, accent)
        self.screen.blit(txt, (gx, gy))

        # --- sub-label ---
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
        notch_alpha=255 if self.hovered else int(200*pulse)
        #pygame.draw.line(screen,(*accent,notch_alpha),(x,y+notch),(x+notch,y),2)
        #tick_alpha=int(140*pulse)
        #pygame.draw.rect(screen,(*accent,tick_alpha),(x,y+h//2-5,3,10))
        #pygame.draw.rect(screen,(*accent,tick_alpha),(x+w-3,y+h//2-5,3,10))
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
               unselected_color=(100,100,100),radius=10):
        self.x = x
        self.y = y
        self.displaywidth=rect_width
        self.text = text
        font_size=int(12/320*rect_width)
        self.font = pygame.font.SysFont(font_name, font_size)
        self.font_box=pygame.font.SysFont(font_name,18)
        self.text_color = text_color
        self.selected_color = selected_color
        self.unselected_color = unselected_color
        self.radius = radius

    def select(self):
        self.selected = True
    def deselect(self):
        self.selected = False

    def draw(self, screen):
        small_rect=pygame.Rect(self.x-self.radius,self.y-self.radius,self.radius*2,self.radius*2)
        if not self.selected:
            pygame.draw.rect(screen,(0,0,255),small_rect,3,2)
        else:
            pygame.draw.rect(screen,(0,0,255),small_rect,0,2)
            num = self.font_box.render(str(self.priority), True, self.text_color)
            screen.blit(num, (self.x-num.get_width()//2, self.y-num.get_height()//2))

        text_surf = self.font.render(self.text, True, self.text_color)
        self.rect=pygame.Rect(self.x-self.radius,self.y-self.radius,self.radius*2+10+text_surf.get_width(),max(self.radius*2,text_surf.get_height()))
        screen.blit(text_surf, (self.x + self.radius + 10, self.y - text_surf.get_height() // 2))

        pygame.draw.circle(screen, self.unselected_color, (self.x+self.displaywidth*0.8, self.y), self.radius, 2)
        self.radiorect=pygame.Rect(self.x+self.displaywidth*0.8-self.radius, self.y-self.radius, self.radius*2,self.radius*2)
        if self.reverse:
            pygame.draw.circle(screen, self.selected_color, (self.x+self.displaywidth*0.8, self.y), self.radius//2)
        
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
        #panel_width=0.4*self.width
        #panel_height=0.8*self.height
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
        self.ldb_but=Button("",0,0,0,0,None)
        self.charts=Button("",0,0,0,0,None)
        self.fig_no=0
        self.b1=Button("",0,0,0,0,None)
        self.b2=Button("",0,0,0,0,None)
        self.priorities=[]
        self.transition = TransitionManager(self.screen)
        self.t0=None
        self.snapshot=None
    def page(self):
        self.screen.blit(self.bg,(0,0))
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
        sy = bar_height*1.1+bar_y
        self.screen.blit(sub, (sx, sy))
            
    def show_results(self,winner,event):
        if self.t0==None:
            self.t0=time.time()
        if winner==0:
            #rect=pygame.Rect((self.width-obj.playing_board.width)//2,(self.height-obj.playing_board.height)//2,obj.playing_board.width,obj.playing_board.height)
            self.draw_results("DRAW")
        elif winner==1:
            #rect=pygame.Rect((self.width-obj.playing_board.width)//2,(self.height-obj.playing_board.height)//2,obj.playing_board.width,obj.playing_board.height)
            self.draw_results("WINNER: "+self.player1)
        else:
            #rect=pygame.Rect((self.width-obj.playing_board.width)//2,(self.height-obj.playing_board.height)//2,obj.playing_board.width,obj.playing_board.height)
            self.draw_results("WINNER: "+self.player2)
        if event.type==pygame.KEYDOWN:
            #print("hello")
            if event.key==pygame.K_SPACE:
                #print("hi")
                return True
        return False

    def show_leaderboard(self,obj,event):
        rect=pygame.Rect((self.width-obj.playing_board.width)//2,(self.height-obj.playing_board.height)//2,obj.playing_board.width,obj.playing_board.height)
        pygame.draw.rect(self.screen, (192,192,192), rect)
        font=pygame.font.SysFont("Consolas",int(rect.w*0.07),bold=True)
        line=font.render("Sort Mode of Leaderboard",True,(255,255,255))
        self.screen.blit(line,pygame.Rect((self.width-line.get_width())//2,int(rect.y+rect.h*0.1),line.get_width(),line.get_height()))
        self.o1.assign(int(rect.w*0.1+rect.x),int(rect.y+0.2*rect.h),rect.w,"Game name lexicographically")
        self.o2.assign(int(rect.w*0.1+rect.x),int(rect.y+0.267*rect.h),rect.w,"Username")
        self.o3.assign(int(rect.w*0.1+rect.x),int(rect.y+0.334*rect.h),rect.w,"No. of Wins")
        self.o4.assign(int(rect.w*0.1+rect.x),int(rect.y+0.401*rect.h),rect.w,"No. of Losses")
        self.o5.assign(int(rect.w*0.1+rect.x),int(rect.y+0.468*rect.h),rect.w,"No. of Draws")
        self.o6.assign(int(rect.w*0.1+rect.x),int(rect.y+0.535*rect.h),rect.w,"Win/Loss ratio")
        self.o7.assign(int(rect.w*0.1+rect.x),int(rect.y+0.602*rect.h),rect.w,"No. of Games played of this type")
        font=pygame.font.SysFont("Consolas",int(rect.w*0.035),bold=True)
        self.ldb_but.assign("Generate",int(0.6*rect.w+rect.x),int(0.75*rect.h+rect.y),int(0.35*rect.w),int(0.2*rect.h),font)
        self.charts.assign("Visualize",int(0.05*rect.w+rect.x),int(rect.y+0.75*rect.h),int(0.45*rect.w),int(0.2*rect.h),font)
        self.o1.draw(self.screen)
        self.o2.draw(self.screen)
        self.o3.draw(self.screen)
        self.o4.draw(self.screen)
        self.o5.draw(self.screen)
        self.o6.draw(self.screen)
        self.o7.draw(self.screen)
        self.ldb_but.draw(self.screen)
        self.charts.draw(self.screen)
        objs=[self.o1,self.o2,self.o3,self.o4,self.o5,self.o6,self.o7]
        rect=[i.rect for i in objs]
        radiorects=[i.radiorect for i in objs]
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            for i in range(7):
                if rect[i].collidepoint(event.pos):
                    if not objs[i].selected:
                        objs[i].selected=True
                        self.priorities.append(objs[i])
                    else:
                        objs[i].selected=False
                        self.priorities.remove(objs[i])
            for i in range(len(self.priorities)):
                self.priorities[i].priority=i+1
            
            for i in range(7):
                if radiorects[i].collidepoint(event.pos):
                    objs[i].reverse=not objs[i].reverse
            

        if self.charts.handle_event(event):
            return True
        if self.ldb_but.handle_event(event):
            preference=[-i.idx if i.reverse else i.idx for i in self.priorities]
            cmd="bash leaderboard.sh"
            for i in preference:
                cmd+=" "+str(i)
            print(cmd)
            os.system(cmd)
        return False

    def draw_gauge(self,ax, values, texts, color):
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
                #print(arr)
                if arr[6]=="TicTacToe":
                    game_counts[0]+=1
                elif arr[6]=="Othello":
                    game_counts[1]+=1
                else:
                    game_counts[2]+=1
        
        #print(game_counts)
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

        # Dark background
        axes[1][0].set_facecolor("#0d1b2a")

        # Axis markings
        axes[1][0].set_xlabel("Players", color="white", fontsize=10)
        axes[1][0].set_ylabel("Wins",    color="white", fontsize=10)
        axes[1][0].set_title("Top 5 Players by Wins", color="white", fontsize=11)
        axes[1][0].tick_params(labelcolor="white")

        # Clean look
        for spine in axes[1][0].spines.values():
            spine.set_visible(False)
        wedges=axes[1][1].pie(game_counts,colors=["#4fc3f7", "#ce93d8", "#80cbc4"],autopct=lambda pct: f'{pct:.1f}%' if pct > 0 else '')[0]
        axes[1][1].legend(
            wedges,
            ["tictactoe", "othello", "connect4"],   # ← your own custom texts
            loc="center left",
            bbox_to_anchor=(1, 0.5), 
            fontsize=8
        )
        return False
    
    def on_close(self,event):
        self.fig_no=-1
    def show_charts(self):
        if self.fig_no == 0:
            self.draw_charts()              # builds charts, no plt.show()
            fig = plt.gcf()
            fig.canvas.mpl_connect('close_event', self.on_close)  # ✅ connect BEFORE show
            self.fig_no = 1
            plt.show()          # ✅ non-blocking, pygame loop continues

        if self.fig_no == -1:
            self.fig_no = 0
            return True
        return False
    
    def show_intermediate(self,obj,event):
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
    con=Connect4(width,height,board.screen)
    o=3
    results=False
    stats=False
    charts=False
    intermediate=False
    fading=False
    final_result=0
    while running:
        event = pygame.event.Event(pygame.NOEVENT)
        key=None
        for event in pygame.event.get():
            if(event.type==pygame.QUIT):
                running=False
            elif(event.type==pygame.VIDEORESIZE and not charts):
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
            elif event.type==pygame.KEYDOWN:
                key=event
        if key==None:
            key=event
        board.page()
        if is_menu:
            o=menu.draw(board.screen,event)
            if(o!=3):
                is_menu=False
                fading=True
                if o==0:
                    board.transition.start(o,"./pictures/tictactoe.png",board)
                elif o==2:
                    board.transition.start(o,"./pictures/connect4.png",board)
                #print("hi")
        else:
            if fading:
                if board.transition.active():
                    #print("hi")
                    board.transition.update()
                else:
                    fading=False
            elif results:
                if board.show_results(final_result,key):
                    results=False
                    stats=True
            elif stats:
                if o==0:
                    obj=tic
                elif o==1:
                    obj=oth
                elif o==2:
                    obj=con
                if board.show_leaderboard(obj,event):
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
                if board.show_intermediate(obj,event):
                    intermediate=False
                    is_menu=True
                    board=Board(board.player1,board.player2,width,height,None)
                    menu=Menu(width,height,board)
                    tic=Tictactoe(width,height,board.screen,player1,player2)
                    oth=Othello(width,height,board.screen)
                    con=Connect4(width,height,board.screen)
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
                changed=obj.play(obj.turn,event)
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
