import pygame
from abc import ABC, abstractmethod
class Button:
    def __init__(self, text, x, y, w, h, font):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = font

        self.base_color = (50, 120, 200)
        self.hover_color = (80, 160, 255)
        self.current_color = self.base_color

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

class Menu:
    def __init__(self,width,height):
        self.width=width
        self.height=height
        self.font=pygame.font.SysFont("Consolas",18)
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


class Board(ABC):
    def __init__(self,player1,player2,width,height,stats):
        self.player1=player1
        self.player2=player2
        self.screen=pygame.display.set_mode((width,height),pygame.RESIZABLE)
        self.stats=stats
        self.width=width
        self.height=height
        self.bg=pygame.image.load("./pictures/background.png")
        self.bg=pygame.transform.scale(self.bg,(self.width,self.height))
    def page(self):
        self.screen.blit(self.bg,(0,0))
    
    def play(self):
        pass
    def win_check(self):
        pass
    def turn_change(self):
        pass

if __name__=="__main__":
    from games.tictactoe import Tictactoe

    pygame.init()
    pygame.display.set_caption("Game Point")
    icon=pygame.transform.scale(pygame.image.load("./pictures/icon.png"),(64,64))
    pygame.display.set_icon(icon)

    width=800
    height=400
    board=Board("a","b",width,height,None)
    menu=Menu(width,height)
    running=True
    is_menu=True
    tic=Tictactoe(width,height,board.screen)
    o=3
    while running:
        event = pygame.event.Event(pygame.NOEVENT)
        for event in pygame.event.get():
            if(event.type==pygame.QUIT):
                running=False
            elif(event.type==pygame.VIDEORESIZE):
                board.width,board.height=event.w,event.h
                board.screen=pygame.display.set_mode((board.width,board.height),pygame.RESIZABLE)
                board.bg=pygame.transform.scale(board.bg,(board.width,board.height))
                menu=Menu(board.width,board.height)
                
        board.page()
        if is_menu:
            o=menu.draw(board.screen,event)
            if(o!=3):
                is_menu=False
        else:
            if(o==0):
                changed=tic.play(tic.turn,event)
                winner=tic.win_check(tic.turn)
                tic.turn_change(changed)
                if winner!="none":
                    if winner=="draw":
                        print("its a draw")
                    else:
                        print("winner is player",winner)
        pygame.display.flip()
    pygame.quit()