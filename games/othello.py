#import statements
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__),'..')) #adds parent dir of file's dir to list of dirs searched by python for importing
from game import Board
import pygame as pg
import numpy as np

class Othello(Board):
	def __init__(self, width, height, screen): #initialise the othello game object
		self.width=width
		self.height=height
		self.screen=screen
		#colors:
		self.bkcolor=(10,10,10) #TODO Changes to be enabled later via settings button
		self.boardcol=(0, 102, 51) #Green TODO settings...
		self.p1tokcol=(211,211,211) #Light gray TODO settings...
		self.p2tokcol=(85,85,85) #Davy's gray TODO settings...
		#tot. number of tokens per player is self.boardsize*self.boardsize/2
		self.p1used=0
		self.p2used=0
		#initialising board, turn number and player turn
		self.boardsize=8 #TODO Allow for ideas like small, medium, large boards
		self.board=np.zeros((self.boardsize, self.boardsize))
		self.turn_num=1
		self.turn_p=1
		min_dim=min(self.width*2/3, self.height) #Right part is for notifications
		pad=0.04*min_dim
		min_dim-=2*pad #removing padding from our calculation for board sizes
		self.sqsize=min_dim/self.boardsize
		#important param for win_check: check that no turns are left for each player.
		self.sk=[0,0]

	#TODO Settings for board colours & player token colours

	def draw_board(self):
		for i in range (self.boardsize):
			x=pad+i*min_dim/self.boardsize+i*pad/8
			for j in range 8:
				y=pad+j*min_dim/self.boardsize+j*pad/8
				rect=pygame.Rect(x, y, self.sqsize, self.sqsize)
				pygame.draw.rect(self.screen, boardcol, rect) #Rect(left, top, width, height) -> Rect
				
				if self.board[i][j]==1:
					pygame.draw.circle(self.screen, self.p1tokcol, rect.center, rect.width//4)
				elif self,board[i][j]==2:
					pygame.draw.circle(self.screen, self.p2tokcol, rect.center, rect.width//4)

	#TODO button for displaying rules.


'''

Othello game rules:
	8x8 board
	centre as:
		W|B
		B|W
	First move:
		Black
	Move definition:
		Add a token of your colour to the board.
		A move is valid only if it traps one or more opponent discs in a straight line between the newly placed disc and an existing own disc
		All trapped discs are flipped to the current player’s colour; multiple lines can be flipped in one move
	If a player has no valid moves, their turn is skipped
	The player with more discs of their colour when no valid moves remain wins

'''

	def turn_change(self, really):
		if really:
			if self.turn_p==2:
				self.turn_num+=1
			self.turn_p=3-self.turn_p

	def validate_pos(self, i, j): #returns dictionary of 8 positions: in each direction, the nearest token of same colour which is not (i,j). If no such token, that position is set to (i,j)
		dest_pos=dict()
		for x in range (i-1, -1, -1): #3 dirns
			#left horizontal:
			if self.board[x][j]==self.turn_p and not dest_pos.__contains__("L"):
				dest_pos["L"]=(x,j)
			#LB: remember, bottom has higher y
			if j+x-i<self.boardsize and self.board[x][j+x-i]==self.turn_p and not dest_pos.__contains__("LB"):
				dest_pos["LB"]=(x,j+x-i)
			#LT
			if j-(x-i)>=0 and self.board[x][j-(x-i)]==self.turn_p and not dest_pos.__contains__("LT"):
				dest_pos["LT"]=(x,j-(x-i))
		#down:
		for y in range(j+1, self.boardsize):
			if self.board[i][y]==self.turn_p: #keycheck not req.d since will break
				dest_pos["B"]=(i, y)
		#up:
		for y in range(j-1, -1, -1):
			if self.board[i][y]==self.turn_p: #keycheck not req.d since will break
				dest_pos["T"]=(i, y)
		for x in range (i+1, self.boardsize): #3 dirns
			#right horizontal:
			if self.board[x][j]==self.turn_p and not dest_pos.__contains__("R"):
				dest_pos["R"]=(x,j)
			#RB
			if j+x-i<self.boardsize and self.board[x][j+x-i]==self.turn_p and not dest_pos.__contains__("RB"):
				dest_pos["RB"]=(x,j+x-i)
			#RT
			if j-(x-i)>=0 and self.board[x][j-(x-i)]==self.turn_p and not dest_pos.__contains__("RT"):
				dest_pos["RT"]=(x,j-(x-i))
		#if not defined, set to (i,j)
		for key in ["L", "LT", 'T', 'RT', 'R', 'RB', 'B', 'LB']:
			if not dest_pos.__contains__(key): dest_pos[key]=(i,j)
		return dest_pos

	def exists_valid(self):
		#Should use validate_pos(i, j)
		for i in range(self.boardsize):
			for j in range(self.boardsize):
				if self.board[i][j]==0 and validate_pos(i,j): return True
		return False

	def get_click_sq(event): #returns false upon invalid event, else returns a tuple (i,j) representing a rectangle.
		if not isinstance(event, pygame.event.Event):
			print('''
Incorrect function call for function play.
Syntax: play(pygame_event)
		 ''')
			return False
		else:
			mx,my=event.pos
			for i in range(self.boardsize):
				x=pad+i*min_dim/self.boardsize+i*pad/8
				for j in range(self.boardsize):
					y=pad+j*min_dim/self.boardsize+j*pad/8
					rect=pygame.Rect(x, y, self.sqsize, self.sqsize)
					if rect.collidepoint(mx, my):
						if self.board[i][j]==0:
							self.board[i][j]=self.turn_p
							return i,j
		return False


	def play(self, event): #returns False if something invalid occurs, else returns true
		draw_board()
		if not exists_valid():
			self.sk[self.turn_p-1]=1
			#turn_change() called in ../game.py
			#TODO implement notification
			return True
		else:
			self.sk[self.turn_p-1]=0
			event_status=get_click_sq(event)
			if not event_status: return False
			i,j=event_status
			if self.board[i][j]==0: return False
			dest_pos=validate_pos(i,j)
			if not dest_pos: return False
			#Flipping: TODO flipping animation
			#Horizontal:
			for x in range(dest_pos['L'][0], dest_pos['R'][0]):
				self.board[x][j]=self.turn_p
			#Vertical:
			for y in range(dest_pos['T'][1], dest_pos['B'][1]):
				self.board[i][y]=self.turn_p
			#Standard diagonal:
			for x in range(dest_pos['LT'][0], dest_pos['RB'][0]):
				self.board[x][j-(x-i)]=self.turn_p
			#Other diagonal:
			for x in range(dest_pos['LB'][0], dest_pos['RT'][0]): #x => left to right
				self.board[x][j+(x-i)]=self.turn_p
			if self.turn_p==1: self.p1used+=1
			else: self.p2used+=1
				#increment self.piused
				#commit turn_change 
			#turn_change() called in ../game.py

	#Gameplay:
		#on turn of player x:
			'''func1: pres line -> bool'''#If exists valid turn: (Loop until valid move played or 3 incorrect moves made.)
				#On event mouseclick (Enable use of game by keyboard?)
				'''func2: pres line -> bool'''#Check1: square should be empty
				'''func3: pres & next line -> bool'''#Check2: Bounds squares of opposite colour in any of the eight directions.
					#For valid check in Check2: commence colour change
					'''func4: pres line -> bool''' #If move invalid, raise some sort of notification for move being invalid, or show some vibration of screen. (TODO: Determine how long notification will be visible)Menu
			#Else:
				#If other player had played in their last turn:
					'''func5: pres line -> bool(success)'''#Notify that no turn is feasible (TODO: Determine how long notification will be visible)
						'''func6: pres line -> bool(success)'''#Can have a sidebar which shows history of such events, ordered by move number.
					#Skip player's present turn.
				#Else:
					#End game
					#Check win condition, return winning player

	def win_check(self):
		''' checks if game over
				then returns winning player (1 or 2)
				In case of draw returns 0
			if game not over return the string "none"
			'''
		if self.sk!=[1,1]: return "none"
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

