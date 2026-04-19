#import statements
from sys import path as sys_path
from os import path as os_path
sys_path.append(os_path.join(os_path.dirname(__file__),'..')) #adds parent dir of file's dir to list of dirs searched by python for importing
from game import Board, Button as ogButton
import pygame as pg
import numpy as np
import time

class comp: #to match with game.py; comp is short for comply/compliance
	def __init__(self, width, height, screen):
		self.height=height
		self.width=width
		self.screen=screen

class Button(ogButton): #Different class because different aesthetic
	def __init__(self, text, x, y, w, h, font):
		super().__init__(text, x, y, w, h, font) #ogButton init stuff
		self.bg=(76, 42, 21)
		self.accent = (212, 175, 55)
		self.dim    = (160, 120, 45)
		self.txtcol=(230, 215, 180)
	#not defining handle_event; to be inheritted
	def polygon(self, notch=12):
		x, y, w, h = self.rect
		notch=int(12/45*h)
		return [
			(x + notch,	     y),
			(x + w-notch,   y),
			(x + w,		 y + notch),
			(x+w,		   y+h-notch),
			(x+w-notch,	     y+h),
			(x+notch,	       y+h),
			(x,			     y + h-notch),
			(x,	      y + notch),
		]


class Othello(Board):
	def __init__(self, width, height, screen, player1, player2): #initialise the othello game object

		self.width=width
		self.height=height
		self.screen=screen
		self.scale=1
		self.abs_scale=1

		#token images:
		self.p2tokimg=pg.image.load("./pictures/white_token.jpg")
		self.p1tokimg=pg.image.load("./pictures/black_token.jpeg")

		#stuff above board
		self.game_name_height=0.09*self.height
		self.gap=0.01*self.height
		self.uname_height=0.10*self.height
		#self.num_ax_height=0.0x*self.height #numbering of columns

		#stuff at left of board
		self.num_ax_width=0.025*self.width
		self.board_log_gap=0.025*self.width
		self.log_right_pad=0.025*self.width

		#initialising board
		self.player1=player1
		self.player1cut=self.player1 #incase uname too long
		self.player2=player2
		self.player2cut=self.player2
		self.boardsize=8
		self.board=np.zeros((self.boardsize, self.boardsize), dtype=int)
		self.board[self.boardsize//2-1][self.boardsize//2-1]=self.board[self.boardsize//2][self.boardsize//2]=2
		self.board[self.boardsize//2-1][self.boardsize//2]=self.board[self.boardsize//2][self.boardsize//2-1]=1
		self.sqimg=pg.image.load("./pictures/square.png")
		self.min_dim=min(self.width*0.6, self.height*0.74) #Right part is for logs
		self.sqpad=0.015*self.min_dim
		self.bottompad=0.04*self.min_dim
		self.min_dim-=(self.boardsize-1)*self.sqpad #gap between squares in board
		self.min_dim-=self.bottompad #removing padding from our calculation for board sizes
		self.sqsize=self.min_dim/self.boardsize

		#Initialise turn number and player turn
		self.turn_num=1
		self.turn=1 #player turn

		#important param for win_check: check that no turns are left for each player.
		self.sk=[0,0]
		self.max_tok=int(self.boardsize*self.boardsize/2) #tot. number of tokens available per player
		self.p1used=0
		self.p2used=0

		#common
		self.font_size=16
		self.bold=pg.font.SysFont("consolas", self.font_size, bold=True)
		self.normal=pg.font.SysFont("consolas", self.font_size)

		#stuff above logs
		#self.gap is same
		self.button_height=0.06*self.height
		self.log_heading_height=0.09*self.height

		#logs surface object
		self.log_x=self.num_ax_width+self.min_dim+self.board_log_gap+(self.boardsize+1)*self.sqpad
		self.log_width=self.width-(self.log_right_pad+self.log_x)
		self.log_y=self.height*0.27
		self.log_height=self.height*0.63
		#log_height will be used while blitting
		self.log_screen=pg.Surface((self.log_width, 1000*self.abs_scale), pg.SRCALPHA)
		#info on this screen will be on a large area to allow scrolling
		#NOTE: not all screens are visible. Visible screens need to be set using pg.display.set_mode(...)
		self.logcol=(50, 28, 10, 180)
		self.log=[]
		self.scroll=0
		self.prev_scroll=0
		self.scroll_sensitivity=100

		#stuff below logs
		self.start_time=time.time()
		self.time_height=0.08*self.height

		#to match with game.py
		self.playing_board=comp(self.min_dim, self.min_dim, self.screen)

		#TODO: Make button for settings, handle clicking in play(), drawing in draw_board and maximize.
		self.settings=Button("Settings", self.log_x, 0.1*self.height, self.log_width*0.475, self.button_height, self.normal)
		self.shown_settings=0

		#Button for help, handled clicking in play(), drawing in draw_board and maximize.
		self.help=Button("Help", self.log_x+self.log_width*0.525, 0.1*self.height, self.log_width*0.475, self.button_height, self.normal)
		self.shown_help=0

	#TODO Settings for board colours, log colours & player token colours

	def draw_game_name(self):
		#bkgrnd
		pg.draw.rect(self.screen, (54, 28, 10), pg.Rect(0, 0, self.width, self.game_name_height))
		pg.draw.line(self.screen, (255, 193, 7), (0, self.game_name_height-1), (self.width, self.game_name_height-1))

		#Nice symbol
		symbol_font = pg.font.SysFont("dejavusans", int(self.game_name_height*0.5))
		symbol=symbol_font.render("✦", True, (255,193,7))
		self.screen.blit(symbol, (4*self.abs_scale, (self.game_name_height-symbol.get_height())//2))

		#Player k's turn
		text_font = pg.font.SysFont("consolas", int(self.game_name_height * 0.28), bold=True)
		text_content=f"Player {'1' if self.turn==1 else '2'}'s Turn"
		text=text_font.render(text_content, True, (255,193,7))
			#Making the capsule
		cw = text.get_width() + 20*self.abs_scale
		ch = text.get_height() + 8*self.abs_scale
		cx = self.width - cw - 8*self.abs_scale
		cy = self.game_name_height// 2 - ch//2
		pg.draw.rect(self.screen, (110, 70, 28), pg.Rect(cx, cy, cw, ch), border_radius=int(ch//2))
		pg.draw.rect(self.screen, (255, 193, 7), pg.Rect(cx, cy, cw, ch), int(1*self.abs_scale), border_radius=int(ch//2))
		self.screen.blit(text, (cx+10*self.abs_scale, int(cy+ch//2)-int(text.get_height()//2)))

		#Game name
		head_font=pg.font.SysFont("georgia", int(0.45*self.game_name_height))
		head=head_font.render("Fangs vs Flames", True, (255,193,7))
		self.screen.blit(head, ((cx-head.get_width())//2,(self.game_name_height-head.get_height())//2))

	def draw_player_names(self):
		p_font=pg.font.SysFont("georgia", int(self.uname_height*0.34), bold=True)
		sub_font = pg.font.SysFont("consolas", int(self.uname_height*0.24))

		for pnum in range(2):
			#namecardbkg
			x=self.num_ax_width+pnum*((self.min_dim+(self.boardsize+1)*self.sqpad)/2+0.005*self.width)
			wid=(self.min_dim+(self.boardsize+1)*self.sqpad)/2-0.005*self.width
			if pnum+1==self.turn: bkg, bordercol=(90, 55, 22),(255,193,7)
			else: bkg, bordercol=(60, 35, 12), (100, 65, 25)
			pg.draw.rect(self.screen, bkg, pg.Rect(x, 0.1*self.height, wid, self.uname_height), border_radius=int(7*self.abs_scale))
			pg.draw.rect(self.screen, bordercol, pg.Rect(x, 0.1*self.height, wid, self.uname_height), int(2*self.abs_scale), border_radius=int(7*self.abs_scale))

			#tokdenote
			d_tok=self.uname_height*0.56
			x_tok_rect=x+self.uname_height*0.15
			y_tok_rect=0.1*self.height+(self.uname_height-d_tok)/2
			rect=pg.Rect(x_tok_rect, y_tok_rect, d_tok, d_tok)

			img=[self.p1tokimg, self.p2tokimg][pnum]
			self.screen.blit(pg.transform.scale(img, (d_tok, d_tok)), rect)

			#the txt
			x_txt=x_tok_rect+d_tok+self.uname_height*0.12
			#y_txt=y_tok_rect
			width_txt=x+wid-x_txt-4*self.abs_scale

			#name
			name=[self.player1, self.player2][pnum]
			if p_font.size(name+'i')[0]>width_txt: #the 'i' is to ensure text doesn't go too close to edge
				name_cut=[self.player1cut, self.player2cut][pnum]
				if p_font.size(name_cut+'i')[0]>width_txt or p_font.size(name_cut+'i')[0]<width_txt:
					lo, hi = 0, len(name) - 2  # -2 reserves room for ".."
					while lo < hi:
						mid = (lo + hi + 1) // 2
						if p_font.size(name[:mid] + "..")[0] <= width_txt:
							lo = mid
						else:
							hi = mid - 1
					name=name[:lo-1]+'...'
					if pnum==0: self.player1cut=name
					else: self.player2cut=name
			show_pname=p_font.render(f'{name}', True, (255,193,0))
			self.screen.blit(show_pname, (x_txt, 0.1*self.height+self.uname_height*0.08))

			#num_tok_remain
			used=[self.p1used, self.p2used][pnum]
			show_sub=sub_font.render(f'{self.max_tok-used} tokens remain', True, (255,193,0))
			self.screen.blit(show_sub, (x_txt, 0.1*self.height+self.uname_height*0.54))

	def draw_board_and_num(self):
		bks1=(40, 22, 8)
		bks2=(80, 50, 20)

		#1st bkgrnd for board
		pg.draw.rect(self.screen, bks1, pg.Rect(self.num_ax_width, self.height*0.24, self.sqpad+self.boardsize*(self.sqsize+self.sqpad), self.sqpad+self.boardsize*(self.sqsize+self.sqpad)), border_radius=int(self.sqsize*0.12))

		#2nd bkgrnd for board
		pg.draw.rect(self.screen, bks2, pg.Rect(self.num_ax_width+2*self.abs_scale, self.height*0.24+2*self.abs_scale, self.sqpad+self.boardsize*(self.sqsize+self.sqpad)-4*self.abs_scale, self.sqpad+self.boardsize*(self.sqsize+self.sqpad)-4*self.abs_scale), border_radius=int(self.sqsize*0.096))

		#board and numbering
		for i in range (self.boardsize):
			x=self.num_ax_width+i*self.min_dim/self.boardsize+(i+1)*self.sqpad
			#horizontal numbering
			num=self.bold.render(f'{i}', True, (255,193,7))
			self.screen.blit(num, (x+self.sqsize//2-num.width//2, 0.20*self.height))
			for j in range (self.boardsize):
				y=self.height*0.24+j*self.min_dim/self.boardsize+(j+1)*self.sqpad
				if (i==0):
					#vertical numbering
					num=self.bold.render(f'{j}', True, (255,193,7))
					off=(self.num_ax_width-num.width)//2 #not checking for this becoming -ve to prevent bleeding of text into board
					self.screen.blit(num, (off, y+self.sqsize//2-num.height//2))
				rect=pg.Rect(x, y, self.sqsize, self.sqsize)
				sq_util=pg.transform.scale(self.sqimg, (rect.width, rect.height))
				self.screen.blit(sq_util, rect)
				
				rect=pg.Rect(rect.center[0]-rect.width*0.40, rect.center[1]-rect.width*0.40, rect.width*0.80, rect.width*0.80)
				if self.board[i][j]==1:
					p1_utiltok=pg.transform.scale(self.p1tokimg, (rect.width, rect.width))
					self.screen.blit(p1_utiltok, rect)
				elif self.board[i][j]==2:
					p2_utiltok=pg.transform.scale(self.p2tokimg, (rect.width, rect.width))
					self.screen.blit(p2_utiltok, rect)

	def draw_buttons(self):
		#for settings:
		self.settings.draw(self.screen)

		#for help:
		self.help.draw(self.screen)

	def draw_game_log_heading(self):
		rect=pg.Rect(self.log_x, 0.17*self.height, self.log_width, self.log_heading_height)
		pg.draw.rect(self.screen, (60, 35, 12), rect, border_radius=int(6*self.abs_scale))
		pg.draw.rect(self.screen, (255, 193, 7), rect, int(self.abs_scale), border_radius=int(6*self.abs_scale))
		log_heading_font=pg.font.SysFont("georgia", int(self.log_heading_height*0.46), bold=True)
		log_header=log_heading_font.render("Move Log", True, (255, 193, 7))
		self.screen.blit(log_header, (self.log_x+(self.log_width-log_header.width)/2, 0.17*self.height+(self.log_heading_height-log_header.height)/2))

	def draw_time(self):
		rect=pg.Rect(self.log_x, 0.91*self.height, self.log_width, self.time_height)
		pg.draw.rect(self.screen, (60, 35, 12), rect, border_radius=int(6*self.abs_scale))
		pg.draw.rect(self.screen, (255, 193, 7), rect, int(self.abs_scale), border_radius=int(6*self.abs_scale))
		t_font=pg.font.SysFont("georgia", int(self.time_height*0.68), bold=True)
		elapsed=time.time()-self.start_time
		formatted=time.strftime("%H:%M:%S", time.gmtime(elapsed))
		samay=t_font.render(formatted,True,(255,193,7))
		self.screen.blit(samay, (self.log_x+(self.log_width-samay.width)/2, 0.91*self.height+(self.time_height-samay.height)/2+2*self.abs_scale))

	def draw_board(self):
		self.draw_game_name()
		self.draw_player_names()
		self.draw_board_and_num()
		self.draw_buttons()
		self.draw_game_log_heading()
		self.draw_time()

	def maximize(self,width,height,screen):
		#fonts
		self.scale=min(width/self.width, height/self.height)
		self.abs_scale*=self.scale
		self.font_size=int(self.font_size*self.scale)
		self.normal=pg.font.SysFont("consolas", self.font_size)
		self.bold=pg.font.SysFont("consolas", self.font_size, bold=True)

		#fundamental attributes
		self.width=width
		self.height=height
		self.screen=screen

		#stuff above board
		self.game_name_height=0.09*self.height
		self.gap=0.01*self.height
		self.uname_height=0.10*self.height

		#stuff at left of board
		self.num_ax_width=0.025*self.width
		self.board_log_gap=0.025*self.width
		self.log_right_pad=0.025*self.width

		#board
		self.min_dim=min(self.width*0.6, self.height*0.74) #Right part is for logs
		self.sqpad=0.015*self.min_dim
		self.bottompad=0.04*self.min_dim
		self.min_dim-=(self.boardsize-1)*self.sqpad #gap between squares in board
		self.min_dim-=self.bottompad #removing padding from our calculation for board sizes
		self.sqsize=self.min_dim/self.boardsize

		#stuff above logs
		#self.gap is same
		self.button_height=0.06*self.height
		self.log_heading_height=0.09*self.height

		#logs surface object
		self.log_x=self.num_ax_width+self.min_dim+self.board_log_gap+(self.boardsize+1)*self.sqpad
		self.log_width=self.width-(self.log_right_pad+self.log_x)
		self.log_y=self.height*0.27
		self.log_height=self.height*0.63
		self.scroll*=self.scale
		self.prev_scroll*=self.scale
		#log_height will be used while blitting
		self.log_screen=pg.Surface((self.log_width, 1000*self.abs_scale), pg.SRCALPHA)

		#stuff below logs
		self.time_height=0.08*self.height

		#for settings
		self.settings=Button("Settings", self.log_x, 0.1*self.height, self.log_width*0.475, self.button_height, self.normal)

		#for help
		self.help=Button("Help", self.log_x+self.log_width*0.525, 0.1*self.height, self.log_width*0.475, self.button_height, self.normal)

#		self.draw_board()
#		self.to_log()
#		self.display_log()

	#TODO button for displaying rules.

	def display_help(self):
		self.log_screen.fill(self.logcol)
		head='Othello game rules:'
		rules='\n8x8 board\n\tcentre as:\n\t\tW|B\n\t\tB|W\n\tFirst move:\n\t\tBlack\n\tMove definition:\n\t\tAdd a token of your colour to the board.\n\t\tA move is valid only if it traps one or more opponent discs in a straight line between the newly placed disc and an existing own disc\n\t\tAll trapped discs are flipped to the current player’s colour; multiple lines can be flipped in one move\n\t\tIf a player has no valid moves, their turn is skipped\n\t\tThe player with more discs of their colour when no valid moves remain wins'
		rules=rules.replace('\t', '    ')
		head_surf=self.bold.render(head, True, (255,255,0), wraplength=int(self.log_width)).convert_alpha()
		main_surf=self.normal.render(rules, True, (255,255,0), wraplength=int(self.log_width)).convert_alpha()
		prev_scroll=self.scroll
		self.scroll=0
		self.log_screen.blit(head_surf, (10, self.scroll))
		self.log_screen.blit(main_surf, (10,self.scroll+head_surf.get_height()))
		self.display_log()
		return prev_scroll

	def to_log(self):
		self.log_screen.fill(self.logcol)
		#blunder alert! putting this in display_log would wipe everything that to_log puts.
		y=10 #init ofset from surface start
		for msg_obj in self.log:
			#msg_obj[1] is a tuple (string, color)
			msg_head="Turn "+str(msg_obj[0][0])+':'
			msg=" Player "+str(msg_obj[0][1])+": "+str(msg_obj[1][0])
			head_surf=self.bold.render(msg_head, True, msg_obj[1][1], wraplength=int(self.log_width)).convert_alpha()
			main_surf=self.normal.render(msg, True, msg_obj[1][1], wraplength=int(self.log_width)).convert_alpha()
			#https://stackoverflow.com/questions/42014195/rendering-text-with-multiple-lines-in-pygame (the answer with 3 votes)
			self.log_screen.blit(head_surf, (10, y))
			y+=head_surf.get_height()
			self.log_screen.blit(main_surf, (10,y))
			y+=(main_surf.get_height()+10)
		if y>self.scroll+self.log_height: self.scroll=y-self.log_height #autoscroll
		return (970-25*self.abs_scale-y<0) #if returns True, pop[0]

	def display_log(self):
		tlc=(self.log_x, self.log_y) #top-left coordinate of log screen
		capture=pg.Rect(0, self.scroll, self.log_width, self.log_height) #Rect(left, top, width, height) -> Rect
		#"Capture" this part of log_screen to blit
		self.screen.blit(self.log_screen, tlc, capture)

	def turn_change(self, really):
		if really:
			if self.turn==2:
				self.turn_num+=1
			self.turn=3-self.turn

	def validate_pos(self, i, j): #returns dictionary of 8 positions: in each direction, the nearest token of same colour which is not (i,j). If no such token, that position is set to (i,j)
		dest_pos=dict()
		encountered=0
		for x in range (i-1, -1, -1): #3 dirns
			#left horizontal:
			if self.board[x][j]==0: break
			elif self.board[x][j]==self.turn:
				if encountered: dest_pos["L"]=(x,j)
				break
			else: encountered=1
		encountered=0
		for x in range (i-1, -1, -1): #3 dirns
			#LT: remember, top has lower y, and x<i and x decreases with steps in loop.
			if j+x-i>=0:
				if self.board[x][j+x-i]==0: break
				elif self.board[x][j+x-i]==self.turn:
					if encountered: dest_pos["LT"]=(x,j+x-i)
					break
				else: encountered=1
		encountered=0
		for x in range (i-1, -1, -1): #3 dirns
			#LB
			if j-(x-i)<self.boardsize:
				if self.board[x][j-(x-i)]==0: break
				elif self.board[x][j-(x-i)]==self.turn:
					if encountered: dest_pos["LB"]=(x,j-(x-i))
					break
				else: encountered=1
		encountered=0
		#down:
		for y in range(j+1, self.boardsize):
			if self.board[i][y]==0: break
			if self.board[i][y]==self.turn: #keycheck not req.d since will break
				if encountered: dest_pos["B"]=(i, y)
				break
			else: encountered=1
		encountered=0
		#up:
		for y in range(j-1, -1, -1):
			if self.board[i][y]==0: break
			if self.board[i][y]==self.turn: #keycheck not req.d since will break
				if encountered: dest_pos["T"]=(i, y)
				break
			else: encountered=1
		encountered=0
		for x in range (i+1, self.boardsize): #3 dirns
			#right horizontal:
			if self.board[x][j]==0: break
			if self.board[x][j]==self.turn:
				if encountered: dest_pos["R"]=(x,j)
				break
			else: encountered=1
		encountered=0
		for x in range (i+1, self.boardsize): #3 dirns
			#RB; x increases here with step & x>i
			if j+x-i<self.boardsize:
				if self.board[x][j+x-i]==0: break
				elif self.board[x][j+x-i]==self.turn:
					if encountered: dest_pos["RB"]=(x,j+x-i)
					break
				else: encountered=1
		encountered=0
		for x in range (i+1, self.boardsize): #3 dirns
			#RT
			if j-(x-i)>=0:
				if self.board[x][j-(x-i)]==0: break
				elif self.board[x][j-(x-i)]==self.turn:
					if encountered: dest_pos["RT"]=(x,j-(x-i))
					break
				else: encountered=1
		#if not defined, set to (i,j)
		if dest_pos==dict(): return False
		for key in ["L", "LT", 'T', 'RT', 'R', 'RB', 'B', 'LB']:
			if not dest_pos.__contains__(key): dest_pos[key]=(i,j)
		return dest_pos

	def exists_valid(self):
		#Should use validate_pos(i, j)
		for i in range(self.boardsize):
			for j in range(self.boardsize):
				if self.board[i][j]==0 and self.validate_pos(i,j): return True
		return False

	def get_click_sq(self, event): #returns False upon invalid event, else returns a tuple (i,j) representing a rectangle.
		mx,my=event.pos
		for i in range(self.boardsize):
			x=self.num_ax_width+i*self.min_dim/self.boardsize+(i+1)*self.sqpad
			for j in range(self.boardsize):
				y=self.height*0.24+j*self.min_dim/self.boardsize+(j+1)*self.sqpad
				rect=pg.Rect(x, y, self.sqsize, self.sqsize)
				if rect.collidepoint(mx, my):
					if self.board[i][j]==0:
						return i,j
		return False


	def play(self, turn, event): #the variable turn is taken just to match game.py
		#returns False if something invalid occurs, else returns true
		self.draw_board()
		if self.shown_help==1:
			self.prev_scroll=self.display_help()
		elif self.shown_help==2:
			self.scroll=self.prev_scroll
			self.shown_help=0 #made the change to prevent self.scroll from getting trapped (3 states were thus required)
			self.to_log()
			self.display_log()
		else:
			self.to_log()
			self.display_log()
		if not self.exists_valid():
			self.log.append(((self.turn_num, self.turn),("No valid turn exists. Skipping...", (255,85,255)))) #colour from ansi escape codes
			to_pop=self.to_log()
			if to_pop: self.log.pop(0)
			self.display_log()
			self.sk[self.turn-1]=1
			#turn_change() called in ../game.py
			#TODO implement notification
			return True
		elif self.settings.handle_event(event):
			self.shown_settings=1-self.shown_settings
			#TODO
		elif self.help.handle_event(event):
			self.shown_help+=1
		elif event.type == pg.MOUSEWHEEL:
			temp=self.scroll
			self.scroll-=event.y*self.scroll_sensitivity
			if not (self.scroll>=0 and self.scroll<=1000*self.abs_scale-self.log_height): self.scroll=temp
		else:
			self.sk[self.turn-1]=0
			if event.type == pg.MOUSEBUTTONDOWN: event_status=self.get_click_sq(event)
			else: return False
			if not event_status: return False
			i,j=event_status
			dest_pos=self.validate_pos(i,j)
			if not dest_pos:
				self.log.append(((self.turn_num, self.turn),(f"Invalid position ({i}, {j})", (255,60,60)))) #again colour from ansi escape codes
				#Consider (255, 85, 85) instead in case of low visibility of this red.
				to_pop=self.to_log()
				if to_pop: self.log.pop(0)
				return False
			self.board[i][j]=self.turn
			#flipping: TODO flipping animation (loops will need modification since not all tokens accessed in loop are of opposite color; own tokens (<=3 of them) need to be excluded.
			#horizontal:
			for x in range(dest_pos['L'][0], dest_pos['R'][0]):
				self.board[x][j]=self.turn
			#vertical:
			for y in range(dest_pos['T'][1], dest_pos['B'][1]):
				self.board[i][y]=self.turn
			#standard diagonal:
			for x in range(dest_pos['LT'][0], dest_pos['RB'][0]):
				self.board[x][j+(x-i)]=self.turn
			#other diagonal:
			for x in range(dest_pos['LB'][0], dest_pos['RT'][0]): #x => left to right
				self.board[x][j-(x-i)]=self.turn
			if self.turn==1: self.p1used+=1
			else: self.p2used+=1
				#increment self.piused
			self.log.append(((self.turn_num, self.turn),(f'Played ({i}, {j}); {self.max_tok-[self.p1used, self.p2used][self.turn-1]} tokens remaining', (0,170,0)))) #again colour from ansi escape codes
			#Consider (85,255,85) instead if low visibility
			to_pop=self.to_log()
			if to_pop: self.log.pop(0)
			return True
				#commit turn_change 
			#turn_change() called in ../game.py

	#Gameplay initial draft:
		#on turn of player x:
			#'''func1: pres line -> bool'''#If exists valid turn: (Loop until valid move played or 3 incorrect moves made.)
				#On event mouseclick (Enable use of game by keyboard?)
				#'''func2: pres line -> bool'''#Check1: square should be empty
				#'''func3: pres & next line -> bool'''#Check2: Bounds squares of opposite colour in any of the eight directions.
					#For valid check in Check2: commence colour change
					#'''func4: pres line -> bool''' #If move invalid, raise some sort of notification for move being invalid, or show some vibration of screen. (TODO: Determine how long notification will be visible)Menu
			#Else:
				#If other player had played in their last turn:
					#'''func5: pres line -> bool(success)'''#Notify that no turn is feasible (TODO: Determine how long notification will be visible)
						#'''func6: pres line -> bool(success)'''#Can have a sidebar which shows history of such events, ordered by move number.
					#Skip player's present turn.
				#Else:
					#End game
					#Check win condition, return winning player

	def win_check(self, turn): #the variable turn is taken just to match game.py
		''' checks if game over
				then returns winning player (1 or 2)
				In case of draw returns 0
			if game not over return the string "none"
			'''
		if self.sk!=[1,1] and self.max_tok not in (self.p1used, self.p2used): return "none"
		c=np.bincount(self.board.ravel())
		if c[1]>c[2]: return 1
		elif c[2]>c[1]: return 2
		else: return 0

	def wipeout(self): #returns winner if wipeout, else returns 0
		if np.all(self.board==1): wiper=1
		elif np.all(self.board==2): wiper=2
		else: wiper=0
	#TODO: manage displaying
		return wiper

