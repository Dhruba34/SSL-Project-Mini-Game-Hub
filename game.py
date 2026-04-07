import pygame
import numpy as np
import time
import os
import sys
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
class Button:
    def __init__(self, text, x, y, w, h, font):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = font

        self.base_color = (50, 120, 200)
        self.hover_color = (80, 160, 255)
        self.current_color = self.base_color
    def assign(self,text,x,y,w,h,font):
        self.rect=pygame.Rect(x,y,w,h)
        self.text=text
        self.font=font
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                self.current_color = self.hover_color
            else:
                self.current_color = self.base_color

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True   # button clicked
        return False

    def draw(self, screen):
        pygame.draw.rect(screen, self.current_color, self.rect, border_radius=12)

        txt_surface = self.font.render(self.text, True, (255, 255, 255))
        screen.blit(
            txt_surface,
            (
                self.rect.x + (self.rect.w - txt_surface.get_width()) // 2,
                self.rect.y + (self.rect.h - txt_surface.get_height()) // 2,
            ),
        )

class Checkbox:
    def __init__(self, x, y, rect_width,text,idx,font_name="Consolas", font_size=22,
                 text_color=(255,255,255), selected_color=(70, 130, 180),
                 unselected_color=(100, 100, 100), radius=10):
        self.x = x
        self.y = y
        self.text = text
        font_size=int(18/320*rect_width)
        self.font = pygame.font.SysFont(font_name, font_size)
        self.text_color = text_color
        self.selected_color = selected_color
        self.unselected_color = unselected_color
        self.radius = radius
        self.selected = False
        self.idx=idx
        self.reverse=False
        self.rect=None
    def assign(self,x,y,rect_width,text,font_name="Consolas",font_size=22,text_color=(255,255,255),selected_color=(70,130,180),
               unselected_color=(100,100,100),radius=10):
        self.x = x
        self.y = y
        self.text = text
        font_size=int(18/320*rect_width)
        self.font = pygame.font.SysFont(font_name, font_size)
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
            num = self.font.render(str(self.priority[self.idx]), True, self.text_color)
            screen.blit(num, (self.x-num.get_width()//2, self.y-num.get_height()//2))

        text_surf = self.font.render(self.text, True, self.text_color)
        self.rect=pygame.Rect(self.x-self.radius,self.y-self.radius,self.radius*2+10+text_surf.get_width(),max(self.radius*2,text_surf.get_height()))
        screen.blit(text_surf, (self.x + self.radius + 10, self.y - text_surf.get_height() // 2))

        pygame.draw.circle(screen, self.unselected_color, (self.x+self.radius+10+text_surf.get_width()+5, self.y), self.radius, 2)
        if self.reverse:
            pygame.draw.circle(screen, self.selected_color, (self.x+self.radius+10+text_surf.get_width()+5, self.y), self.radius // 2 + 2)
        
class Menu:
    def __init__(self,width,height):
        self.width=width
        self.height=height
        self.font=pygame.font.SysFont("Consolas",int(min(18/800*width,18/400*height)))
        self.tictactoe=Button("TicTacToe",0.4*width,0.2*height,0.2*width,0.15*height,self.font)
        self.othello=Button("Othello",0.4*width,0.4*height,0.2*width,0.15*height,self.font)
        self.connect4=Button("Connect4",0.4*width,0.6*height,0.2*width,0.15*height,self.font)
    def draw(self,screen,event):
        panel_width=0.4*self.width
        panel_height=0.8*self.height
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill((10, 10, 10, 160))
        panel_rect = panel_surface.get_rect()
        panel_rect.center = (self.width // 2, self.height // 2)
        color = (0, 0, 0)
        pygame.draw.rect(screen, color, panel_rect, border_radius=8)
        self.tictactoe.draw(screen)
        self.othello.draw(screen)
        self.connect4.draw(screen)
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
        self.bg=pygame.image.load("./pictures/background.png")
        self.bg=pygame.transform.scale(self.bg,(self.width,self.height))
        self.leaderboard=Button("",0,0,0,0,None)
        self.board=None
        self.o1=Checkbox(0,0,0,"",0)
        self.o2=Checkbox(0,0,0,"",1)
        self.o3=Checkbox(0,0,0,"",2)
        self.o4=Checkbox(0,0,0,"",3)
        self.o5=Checkbox(0,0,0,"",4)
        self.o6=Checkbox(0,0,0,"",5)
        self.o7=Checkbox(0,0,0,"",6)
        self.ldb_but=Button("",0,0,0,0,None)
        self.charts=Button("",0,0,0,0,None)
        self.fig_no=0
        self.b1=Button("",0,0,0,0,None)
        self.b2=Button("",0,0,0,0,None)
    def page(self):
        self.screen.blit(self.bg,(0,0))
    
    def draw_results(self,rect,text,color,text_color,event,font1="Consolas",size=30):
        pygame.draw.rect(self.screen, color, rect)
        font = pygame.font.SysFont(font1, size, bold=True)
        line1 = font.render("Game Over!", True, text_color)
        line2 = font.render(text, True, text_color)
        x,y,w,h=rect.x,rect.y,rect.w,rect.h
        line1_rect = pygame.Rect(x+int(w*0.25),y+int(0.1*h),w//2,h//4)
        line2_rect = pygame.Rect(x+w//4,y+h//2,int(w*0.75),h//4)
        self.screen.blit(line1, line1_rect)
        self.screen.blit(line2, line2_rect)
        font=pygame.font.SysFont(font1,int(size*0.5),bold=True)
        self.leaderboard.assign("Leaderboard",int(x+0.5*w),int(y+0.7*h),int(w*0.4),int(h*0.2),font)
        self.leaderboard.draw(self.screen)
        return self.leaderboard.handle_event(event)
        
    def show_results(self,winner,obj,event):
        check=False
        if winner==0:
            rect=pygame.Rect((self.width-obj.playing_board.width)//2,(self.height-obj.playing_board.height)//2,obj.playing_board.width,obj.playing_board.height)
            check=self.draw_results(rect,"DRAW",(192,192,192),(255,255,255),event,size=int(0.1*obj.playing_board.width))
        elif winner==1:
            rect=pygame.Rect((self.width-obj.playing_board.width)//2,(self.height-obj.playing_board.height)//2,obj.playing_board.width,obj.playing_board.height)
            check=self.draw_results(rect,"WINNER: "+self.player1,(192,192,192),(255,255,255),event,size=int(0.1*obj.playing_board.width))
        else:
            rect=pygame.Rect((self.width-obj.playing_board.width)//2,(self.height-obj.playing_board.height)//2,obj.playing_board.width,obj.playing_board.height)
            check=self.draw_results(rect,"WINNER: "+self.player2,(192,192,192),(255,255,255),event,size=int(0.1*obj.playing_board.width))
        return check

    def show_leaderboard(self,obj,event):
        #the logic is currently faulty. Needs to be updated
        rect=pygame.Rect((self.width-obj.playing_board.width)//2,(self.height-obj.playing_board.height)//2,obj.playing_board.width,obj.playing_board.height)
        pygame.draw.rect(self.screen, (192,192,192), rect)
        font=pygame.font.SysFont("Consolas",int(rect.w*0.07),bold=True)
        line=font.render("Sort Mode of Leaderboard",True,(255,255,255))
        self.screen.blit(line,pygame.Rect((self.width-line.get_width())//2,int(rect.y+rect.h*0.1),line.get_width(),line.get_height()))
        self.o1.assign(int(rect.w*0.3+rect.x),int(rect.y+0.2*rect.h),rect.w,"Grouping games lexicographically")
        self.o2.assign(int(rect.w*0.3+rect.x),int(rect.y+0.267*rect.h),rect.w,"Username")
        self.o3.assign(int(rect.w*0.3+rect.x),int(rect.y+0.334*rect.h),rect.w,"No. of Wins")
        self.o4.assign(int(rect.w*0.3+rect.x),int(rect.y+0.401*rect.h),rect.w,"No. of Losses")
        self.o5.assign(int(rect.w*0.3+rect.x),int(rect.y+0.468*rect.h),rect.w,"No. of Draws")
        self.o6.assign(int(rect.w*0.3+rect.x),int(rect.y+0.535*rect.h),rect.w,"Win/Loss ratio")
        self.o7.assign(int(rect.w*0.3+rect.x),int(rect.y+0.602*rect.h),rect.w,"No. of Games played of this type")
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
        rect1=self.o1.rect
        rect2=self.o2.rect
        rect3=self.o3.rect
        if event.type == pygame.MOUSEBUTTONDOWN:
            if rect1.collidepoint(event.pos):
                self.o1.select()
                self.o2.deselect()
                self.o3.deselect()
            elif rect2.collidepoint(event.pos):
                self.o1.deselect()
                self.o2.select()
                self.o3.deselect()
            elif rect3.collidepoint(event.pos):
                self.o1.deselect()
                self.o2.deselect()
                self.o3.select()
        if self.charts.handle_event(event):
            return True
        if self.ldb_but.handle_event(event):
            if(self.o1.selected):
                os.system("bash leaderboard.sh win")
            elif(self.o2.selected):
                os.system("bash leaderboard.sh loss")
            else:
                os.system("bash leaderboard.sh ratio")
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
    menu=Menu(width,height)
    running=True
    is_menu=True
    tic=Tictactoe(width,height,board.screen)
    oth=Othello(width,height,board.screen)
    con=Connect4(width,height,board.screen)
    o=3
    results=False
    stats=False
    charts=False
    intermediate=False
    final_result=0
    while running:
        event = pygame.event.Event(pygame.NOEVENT)
        for event in pygame.event.get():
            if(event.type==pygame.QUIT):
                running=False
            elif(event.type==pygame.VIDEORESIZE and not charts):
                board.width,board.height=event.w,event.h
                board.screen=pygame.display.set_mode((board.width,board.height),pygame.RESIZABLE)
                board.bg=pygame.transform.scale(board.bg,(board.width,board.height))
                menu=Menu(board.width,board.height)
                tic.maximize(board.width,board.height,board.screen)
                oth.maximize(board.width,board.height,board.screen)
                con.maximize(board.width,board.height,board.screen)
                pygame.display.flip()
                continue
            board.page()
            if is_menu:
                o=menu.draw(board.screen,event)
                if(o!=3):
                    is_menu=False
            else:
                if results:
                    if o==0:
                        obj=tic
                    elif o==1:
                        obj=oth
                    elif o==2:
                        obj=con
                    if board.show_results(final_result,obj,event):
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
                        menu=Menu(width,height)
                        tic=Tictactoe(width,height,board.screen)
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
