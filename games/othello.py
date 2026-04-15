#import statements
from sys import path as sys_path
from os import path as os_path
sys_path.append(os_path.join(os_path.dirname(__file__),'..')) #adds parent dir of file's dir to list of dirs searched by python for importing
from game import Board, Button
import pygame as pg
import numpy as np

class comp: #to match with game.py; comp is short for comply/compliance
	def __init__(self, width, height, screen):
		self.height=height
		self.width=width
		self.screen=screen

class Othello(Board):
	def __init__(self, width, height, screen, player1, player2): #initialise the othello game object

		self.width=width
		self.height=height
		self.screen=screen
		self.scale=1

		#colors:
		self.bkcolor=(10,10,10) #TODO Changes to be enabled later via settings button
		self.boardcol=(0, 102, 51) #Green TODO settings...
		self.p2tokcol=(255,255,255) #white TODO settings...
		self.p1tokcol=(0,0,0) #Davy's gray TODO settings...

		#initialising board
		self.player1=player1
		self.player2=player2
		self.boardsize=4 #TODO Allow for ideas like small, medium, large boards
		self.board=np.zeros((self.boardsize, self.boardsize), dtype=int)
		self.board[self.boardsize//2-1][self.boardsize//2-1]=self.board[self.boardsize//2][self.boardsize//2]=2
		self.board[self.boardsize//2-1][self.boardsize//2]=self.board[self.boardsize//2][self.boardsize//2-1]=1
		self.min_dim=min(self.width*2/3, self.height*0.92) #Right part is for logs
		self.pad=0.04*self.min_dim
		self.min_dim-=(self.boardsize-1)*self.pad/8 #gap between squares in board
		self.min_dim-=2*self.pad #removing padding from our calculation for board sizes
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

		#logs surface object
		self.log_width=self.width-self.min_dim-3*self.pad-self.boardsize*self.pad/8
		self.log_height=self.height-2*self.pad-self.min_dim/8 #last term is due to button, not due to board.
		#log_height will be used while blitting
		self.log_screen=pg.Surface((self.log_width, 1000*self.scale))
		#self.log_screen.set_alpha(170)
		#info on this screen will be on a large area to allow scrolling
		#NOTE: not all screens are visible. Visible screens need to be set using pg.display.set_mode(...)
		self.logcol=(30,30,30)
		self.log=[]
		self.scroll=0
		self.scroll_sensitivity=100

		#to match with game.py
		self.playing_board=comp(self.min_dim, self.min_dim, self.screen)

		#TODO: Make button for settings, handle clicking in play(), drawing in draw_board and maximize.
		self.settings=Button("Settings", 2*self.pad+self.min_dim+self.boardsize*self.pad/8, self.pad, self.log_width/2, self.min_dim/8, self.normal)
		self.shown_settings=0

		#Butto for help, handle clicking in play(), drawing in draw_board and maximize.
		self.help=Button("Help", 2*self.pad+self.min_dim+self.boardsize*self.pad/8+self.log_width/2, self.pad, self.log_width/2, self.min_dim/8, self.normal)
		self.shown_help=0

	#TODO Settings for board colours, log colours & player token colours

	def draw_board(self):
		#TODO: Make button for rules, handle clicking in main.
		for i in range (self.boardsize):
			x=self.pad+i*self.min_dim/self.boardsize+i*self.pad/8
			#horizontal numbering
			num=self.bold.render(f'{i}', True, (255,193,7))
			self.screen.blit(num, (x+self.sqsize//2-num.width//2, 2*self.pad))
			for j in range (self.boardsize):
				y=self.height*0.08+self.pad+j*self.min_dim/self.boardsize+j*self.pad/8
				if (i==0):
					#vertical numbering
					num=self.bold.render(f'{j}', True, (255,193,7))
					off=(self.pad-num.width)//2 #not checking for this becoming -ve to prevent bleeding of text into board
					self.screen.blit(num, (off, y+self.sqsize//2-num.height//2))
				rect=pg.Rect(x, y, self.sqsize, self.sqsize)
				pg.draw.rect(self.screen, self.boardcol, rect) #Rect(left, top, width, height) -> Rect
				
				if self.board[i][j]==1:
					pg.draw.circle(self.screen, self.p1tokcol, rect.center, rect.width//4)
				elif self.board[i][j]==2:
					pg.draw.circle(self.screen, self.p2tokcol, rect.center, rect.width//4)

		#for settings:
		self.settings.draw(self.screen)

		#for help:
		self.help.draw(self.screen)

	def maximize(self,width,height,screen):
		#fonts
		self.scale=min(width/self.width, height/self.height)
		self.font_size=int(self.font_size*self.scale)
		self.normal=pg.font.SysFont("consolas", self.font_size)
		self.bold=pg.font.SysFont("consolas", self.font_size, bold=True)

		self.width=width
		self.height=height
		self.screen=screen
		self.min_dim=min(self.width*2/3, self.height*0.92) #Right part is for logs
		self.pad=0.04*self.min_dim
		self.min_dim-=(self.boardsize-1)*self.pad/8 #gap between squares in board
		self.min_dim-=2*self.pad #removing padding from our calculation for board sizes
		self.sqsize=self.min_dim/self.boardsize
		self.draw_board()

		#for log
		self.log_width=self.width-self.min_dim-3*self.pad-self.boardsize*self.pad/8
		self.log_height=self.height-2*self.pad-self.min_dim/8 #last term is due to button, not due to board.
		#log_height will be used while blitting
		temp=self.log_height
		self.scroll=max(self.scroll-(self.log_height-temp), 0)
		self.log_screen=pg.Surface((self.log_width, 1000*self.scale)) #info on this screen will be on a large area to allow scrolling
		#self.log_screen.set_alpha(170)
		self.to_log()
		self.display_log()

		#for settings
		self.settings=Button("Settings", 2*self.pad+self.min_dim+self.boardsize*self.pad/8, self.pad, self.log_width/2, self.min_dim/8, self.normal)
		self.settings.draw(self.screen)

		#for help
		self.help=Button("Help", 2*self.pad+self.min_dim+self.boardsize*self.pad/8+self.log_width/2, self.pad, self.log_width/2, self.min_dim/8, self.normal)
		self.help.draw(self.screen)

	#TODO button for displaying rules.

	def display_help(self):
		self.log_screen.fill(self.logcol)
		head='Othello game rules:'
		rules='\n8x8 board\n\tcentre as:\n\t\tW|B\n\t\tB|W\n\tFirst move:\n\t\tBlack\n\tMove definition:\n\t\tAdd a token of your colour to the board.\n\t\tA move is valid only if it traps one or more opponent discs in a straight line between the newly placed disc and an existing own disc\n\t\tAll trapped discs are flipped to the current player’s colour; multiple lines can be flipped in one move\n\t\tIf a player has no valid moves, their turn is skipped\n\t\tThe player with more discs of their colour when no valid moves remain wins'
		rules=rules.replace('\t', '    ')
		head_surf=self.bold.render(head, True, (255,255,0), wraplength=int(self.log_width))
		main_surf=self.normal.render(rules, True, (255,255,0), wraplength=int(self.log_width))
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
			head_surf=self.bold.render(msg_head, True, msg_obj[1][1], wraplength=int(self.log_width))
			main_surf=self.normal.render(msg, True, msg_obj[1][1], wraplength=int(self.log_width))
			#https://stackoverflow.com/questions/42014195/rendering-text-with-multiple-lines-in-pygame (the answer with 3 votes)
			self.log_screen.blit(head_surf, (10, y))
			y+=head_surf.get_height()
			self.log_screen.blit(main_surf, (10,y))
			y+=(main_surf.get_height()+10)
		if y>self.scroll+self.log_height: self.scroll=y-self.log_height #autoscroll
		return (970-25*self.scale-y<0) #if returns True, pop[0]

	def display_log(self):
		tlc=(2*self.pad+self.min_dim+self.boardsize*self.pad/8, self.height-self.log_height-self.pad) #top-left coordinate of log screen
		capture=pg.Rect(0, self.scroll, self.log_width, self.log_height) #Rect(left, top, width, height) -> Rect
		#"Capture" this part of log_screen to blit
		self.screen.blit(self.log_screen, tlc, capture)

	def turn_change(self, really):
		if really:
			if self.turn==2:
				self.turn_num+=1
			self.turn=3-self.turn
		#TODO: animation
		name=[self.player1, self.player2][self.turn-1]
		max_len=int(self.min_dim*(1+(self.boardsize-1)/8)/self.font_size)
		if len(name)<=max_len:
			show_pname=self.bold.render(f'{name}', True, (255,193,0))
		else:
			show_pname=self.bold.render(f'{name}'[:max_len-3]+'...', True, (32, 201, 151))
		self.screen.blit(show_pname, (self.pad, self.pad))

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
			x=self.pad+i*self.min_dim/self.boardsize+i*self.pad/8
			for j in range(self.boardsize):
				y=self.height*0.08+self.pad+j*self.min_dim/self.boardsize+j*self.pad/8
				rect=pg.Rect(x, y, self.sqsize, self.sqsize)
				if rect.collidepoint(mx, my):
					if self.board[i][j]==0:
						return i,j
		return False


	def play(self, turn, event): #the variable turn is taken just to match game.py
		#returns False if something invalid occurs, else returns true
		self.draw_board()
		self.display_log() #important because otherwise log erased by drawing board.
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
			prev_scroll=0
			self.shown_help=1-self.shown_help
			if self.shown_help:
				prev_scroll=self.display_help()
			else:
				self.scroll=prev_scroll
				self.to_log()
				self.display_log()
		elif event.type == pg.MOUSEWHEEL:
			temp=self.scroll
			self.scroll-=event.y*self.scroll_sensitivity
			if not (self.scroll>=0 and self.scroll<=1000*self.scale-self.log_height): self.scroll=temp
		else:
			self.sk[self.turn-1]=0
			if event.type == pg.MOUSEBUTTONDOWN: event_status=self.get_click_sq(event)
			else: return False
			if not event_status: return False
			i,j=event_status
			dest_pos=self.validate_pos(i,j)
			if not dest_pos:
				self.log.append(((self.turn_num, self.turn),(f"Invalid position ({i}, {j})", (170, 0, 0)))) #again colour from ansi escape codes
				#Consider (255, 85, 85) instead in case of low visibility of this red.
				to_pop=self.to_log()
				if to_pop: self.log.pop(0)
				self.display_log()
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
			self.log.append(((self.turn_num, self.turn),(f'Placed token at ({i}, {j}); {self.max_tok-[self.p1used, self.p2used][self.turn-1]} tokens remaining', (0,170,0)))) #again colour from ansi escape codes
			#Consider (85,255,85) instead if low visibility
			to_pop=self.to_log()
			if to_pop: self.log.pop(0)
			self.display_log()
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

