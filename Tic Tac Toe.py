from scene import *
import random
import time


class Board (object):
	def __init__(self):
		self.board = [' ' for i in range(9)]
		
	def allEqual(self, val, *args):
		return all(val == self[arg] for arg in args)
		
	def hasWon(self, player):
		rows = [(0, 1, 2), (3, 4, 5), (6, 7, 8),  # horizontal
				(0, 3, 6), (1, 4, 7), (2, 5, 8),  # vertical
				(0, 4, 8), (2, 4, 6)]  # diagonal
				
		for row in rows:
			if self.allEqual(player, *row):
				return row
			
		return False
			
	def canWin(self, player, possibleMove):
		if self[possibleMove] in ['X', 'O']:
			return False
		
		# temporarily assign that value, then check if the player has won
		self[possibleMove] = player
		won = self.hasWon(player)
		self[possibleMove] = ' '
		
		return won
		
	def emptySquares(self):
		empty = []
		for i in range(9):
			if self[i] == ' ':
				empty.append(i)
		return empty
			
	def __getitem__(self, key):
		return self.board[key]

	def __setitem__(self, key, value):
		self.board[key] = value
		
	def __contains__(self, item):
		return item in self.board
		
	def __str__(self):
		return ''.join(self.board)


class Game (Scene):
	def setup(self):
		self.board = Board()
		self.state = 'Menu'
		self.colour = 0
		self.players = {'X': 'Computer', 'O': 'Player'}
		self.difficulties = {'X': 'Easy', 'O': 'Easy'}
		self.computerThinkTime = 1  # in seconds
		self.endThinkTime = None
		self.turn = 1
		self.highlighted = [False for i in range(9)]
		self.lw = self.size.w * 0.05  # width of a line on the board
		
		# Text Settings
		self.ipad = self.size.w > 400
		self.titlef = 'Zapfino'
		self.f = 'Futura'
		
		self.largeS = 30
		self.normalS = 25
		
		if self.ipad:
			self.largeS *= 1.5
			self.normalS *= 1.5
		
	def drawBoard(self):
		w = self.size.w
		h = self.size.h
		
		lw = w * 0.05  # width of a line on the board
		sw = (w - (lw * 2)) / 3  # width of a square
		yo = (h - w) / 2  # y offset of the board from the bottom of the screen
		
		# Black square
		fill(0, 0, 0)
		rect(0, yo, w, w)
		
		fill(1, 1, 1)
		# Horizontal Lines
		rect(0, yo + sw, w, lw)
		rect(0, h - (yo + sw + lw), w, lw)
		# Vertical Lines
		rect(sw, yo, lw, w)
		rect(w - (sw + lw), yo, lw, w)
		
		for square in range(9):
			x = square % 3
			y = int(square / 3)
			tint((1, 0, 0) if self.highlighted[square] else (1, 1, 1))
			textX = (sw * x) + (lw * x) + (sw / 2)
			textY = (sw * y) + (lw * y) + (sw / 2) + yo
			text(self.board[square], self.f, 115 if self.ipad else 70, textX, textY)
	
	def draw(self):
		w = self.size.w
		h = self.size.h
		
		background(*self.getColour(self.colour))
		self.colour = (self.colour + 0.0016) % 1
			
		tint(*(1 - c for c in self.getColour(self.colour)))
		
		if self.state == 'Menu':
			text('Tic-Tac-Toe', self.titlef, self.largeS, w * 0.5, h * 0.9)
			text('Play', self.f, self.largeS, w * 0.5, h * 0.6)
		
		elif self.state == 'Player Select':
			text('Player Select', self.titlef, self.largeS, w * 0.5, h * 0.9)
			text('X: ' + self.players['X'], self.f, self.normalS, w * 0.5, h * 0.63)
			text('O: ' + self.players['O'], self.f, self.normalS, w * 0.5, h * 0.38)
			
			if 'Computer' not in self.players.values():
				playOrContinue = 'Play'
			else:
				playOrContinue = 'Continue'
			text(playOrContinue, self.f, self.normalS, w - 5, 0, alignment=7)
			text('Menu', self.f, self.normalS, 5, 0, alignment=9)
			
		elif self.state.endswith('Difficulty'):
			player = self.state[0]
			text('Player Select', self.titlef, self.largeS, w * 0.5, h * 0.9)
			text('Select the difficulty', self.f, self.normalS, w * 0.5, h * 0.7)
			text('for player %s.' % player, self.f, self.normalS, w * 0.5, h * 0.65)
			text('Easy', self.f, self.normalS, w * 0.5, h * 0.5)
			text('Medium', self.f, self.normalS, w * 0.5, h * 0.42)
			text('Hard', self.f, self.normalS, w * 0.5, h * 0.35)
			text('Expert', self.f, self.normalS, w * 0.5, h * 0.27)
			d = self.difficulties[player]
			text('Current Difficulty: ' + d, self.f, self.normalS, w * 0.5, h * 0.13)
			text('Menu', 'Futura', self.normalS, 5, 0, alignment=9)
			
			if player == 'X' and self.players['O'] == 'Computer':
				playOrContinue = 'Continue'
			else:
				playOrContinue = 'Play'
			text(playOrContinue, self.f, self.normalS, w - 5, 0, alignment=7)
			
		elif self.state == 'Play':
			background(0, 0, 0)
			
			tint(1, 1, 1)
			text('Tic-Tac-Toe', self.titlef, self.largeS, w * 0.5, h * 0.9)
			
			self.drawBoard()
			
			tint(1, 1, 1)
			text('Menu', self.f, self.normalS, 5, 0, alignment=9)
			
			if self.turn > 9:
				self.state = 'Tie'
			
			currentPlayer = 'X' if self.turn % 2 == 1 else 'O'
			
			if self.players[currentPlayer] == 'Computer':
				if self.endThinkTime is None:
					self.endThinkTime = time.time() + self.computerThinkTime
						
				if time.time() > self.endThinkTime:
					self.board[self.computerMove(currentPlayer)] = currentPlayer
					self.turn += 1
					self.endThinkTime = None
					
					row = self.board.hasWon(currentPlayer)
					if row:
						self.state = currentPlayer + ' Wins'
						self.highlight(*row)
						
		elif self.state.endswith('Wins'):
			text(self.state[0] + ' Wins!', self.titlef, self.largeS, w * 0.5, h * 0.9)
			text('Menu', self.f, self.normalS, 5, 0, alignment=9)
			text('Play Again', self.f, self.normalS, w - 5, 0, alignment=7)
			self.drawBoard()
										
		elif self.state == 'Tie':
			text('Tie', self.titlef, self.largeS, w * 0.5, h * 0.9)
			text('Menu', self.f, self.normalS, 5, 0, alignment=9)
			text('Play Again', self.f, self.normalS, w - 5, 0, alignment=7)
			
			self.drawBoard()
		
	def getColour(self, colour):
		colour *= 6
		
		if 0 < colour < 1:
			return [1, colour, 0]
			
		elif 1 <= colour < 2:
			return [1 - (colour % 1), 1, 0]
			
		elif 2 <= colour < 3:
			return [0, 1, (colour % 1)]
			
		elif 3 <= colour < 4:
			return [0, 1 - (colour % 1), 1]
			
		elif 4 <= colour < 5:
			return [(colour % 1), 0, 1]
			
		elif 5 <= colour < 6:
			return [1, 0, 1 - (colour % 1)]
			
		return [1, 0, 0]
		
	def startGame(self):
		self.state = 'Play'
		self.turn = 1
		self.board = Board()
		self.unhighlightAll()
		self.endThinkTime = None
		
	def touch_began(self, touch):
		
		w = self.size.w
		h = self.size.h
		l = touch.location
		
		def touchingText(x, y, width, height):
			if self.ipad:
				width *= 1.5
				height *= 1.5
			return l in Rect(w * x - width / 2, h * y - height / 2, width, height)
		
		if l in Rect(0, 0, 100, 60):
			self.state = 'Menu'
		
		if self.state == 'Menu':
			if touchingText(0.5, 0.6, 100, 60):
				self.state = 'Player Select'
				
		elif self.state == 'Player Select':
			if touchingText(0.5, 0.38, w * 0.5, h * 0.08):
				if self.players['O'] == 'Player':
					self.players['O'] = 'Computer'
				else:
					self.players['O'] = 'Player'
					
			if touchingText(0.5, 0.63, w * 0.5, h * 0.08):
				if self.players['X'] == 'Player':
					self.players['X'] = 'Computer'
				else:
					self.players['X'] = 'Player'
					
			if touchingText(0.88, 0.03, 100, 60):
				if self.players['X'] == 'Computer':
					self.state = 'X Difficulty'
				elif self.players['O'] == 'Computer':
					self.state = 'O Difficulty'
				else:
					self.startGame()
					
		elif self.state.endswith('Difficulty'):
			player = self.state[0]
			
			if touchingText(0.5, 0.5, 100, 40):
				self.difficulties[player] = 'Easy'
				
			if touchingText(0.5, 0.42, 100, 40):
				self.difficulties[player] = 'Medium'
				
			if touchingText(0.5, 0.35, 100, 40):
				self.difficulties[player] = 'Hard'
				
			if touchingText(0.5, 0.27, 100, 40):
				self.difficulties[player] = 'Expert'
				
			if touchingText(0.88, 0.03, 100, 60):
				if player == 'X' and self.players['O'] == 'Computer':
					self.state = 'O Difficulty'
				else:
					self.startGame()
		
		elif self.state == 'Play':
			player = 'X' if self.turn % 2 == 1 else 'O'
			if self.players[player] == 'Player':
				lw = self.lw
				sw = (w - (lw * 2)) / 3  # width of a square
				yo = (h - w) / 2  # y offset of the board from the bottom of the screen
				
				touched = None  # the square touched by the player
				for x in range(3):
					for y in range(3):
						if l in Rect((lw * x) + (sw * x), yo + (lw * y) + (sw * y), sw, sw):
							touched = y * 3 + x
							
				if touched is not None and self.board[touched] == ' ':
					self.board[touched] = player
					self.turn += 1
				
					row = self.board.hasWon(player)
					if row:
						self.state = player + ' Wins'
						self.highlight(*row)
							
		elif self.state in ['X Wins', 'O Wins', 'Tie']:
			if touchingText(0.8, 0.03, 100, 60):
				self.startGame()
			
	def computerMove(self, player):
		if self.difficulties[player] == 'Easy':
			return self.computerEasy(player)
		
		if self.difficulties[player] == 'Medium':
			return self.computerMedium(player)
			
		if self.difficulties[player] == 'Hard':
			return self.computerHard(player)
			
		if self.difficulties[player] == 'Expert':
			return self.computerExpert(player)
			
	def computerEasy(self, player):
		'''Chooses a random available move.'''
		return random.choice(self.board.emptySquares())
			
	def computerMedium(self, player):
		'''First checks to see if the computer can win
		the game, otherwise chooses a random move.'''
		for i in range(9):
			if self.board.canWin(player, i):
				return i
				
		return random.choice(self.board.emptySquares())
			
	def computerHard(self, player):
		'''First checks to see if the computer can win, then check to see if the
		opponent can win and if so, block them. Otherwise, choose a random square,
		prioritizing centre, then corners, then edges.'''
		opponent = 'X' if player == 'O' else 'O'
		
		for i in range(9):
			if self.board.canWin(player, i):
				return i
				
		for i in range(9):
			if self.board.canWin(opponent, i):
				return i
				
		groups = [(4,), (0, 2, 6, 8), (1, 3, 5, 7)]  # centre, corners, edges
		for group in groups:
			# get a set of all empty squares in the group
			possible = set(self.board.emptySquares()).intersection(group)
			if len(possible) > 0:
				return random.choice(list(possible))
			
	def computerExpert(self, player):
		'''First checks to see if the computer can win, then check to see if the
		opponent can win and if so, block them. Otherwise, choose the best possible
		move using the bestXMove and bestOMove functions.'''
		opponent = 'X' if player == 'O' else 'O'
					
		for i in range(9):
			if self.board.canWin(player, i):
				return i
				
		for i in range(9):
			if self.board.canWin(opponent, i):
				return i
				
		# If there's only one square left, choose it
		empty = self.board.emptySquares()
		if len(empty) == 1:
			return empty[0]
		
		return self.bestXMove() if player == 'X' else self.bestOMove()
		
	def bestXMove(self):
		'''Uses hard-coded data to find the best move for X in a given situation.
		Assumes that the computer has already checked for ways to win and ways to
		block the opponent, and that all previous moves have been chosen in the
		same way.'''
		b = str(self.board)
					
		if b == '         ':
			return 0
			
		if b in ['X  O     ', 'X   O    ', 'X     O  ']:
			return 1
			
		if b in ['X      O ', 'X       O']:
			return 2
			
		if b in ['XO       ', 'X O      ']:
			return 3
			
		if b in ['X    O   ', 'XO X  O  ', 'XXOO     ']:
			return 4
			
		if b == 'XOX     O':
			return 6
		
	def bestOMove(self):
		'''Uses hard-coded data to find the best move for O in a given situation.
		Assumes that the computer has already checked for ways to win and ways to
		block the opponent, and that all previous moves have been chosen in the
		same way.'''
		b = str(self.board)
		
		# Some states are not included in the following lists because
		# the game will end in a tie no matter what the computer chooses.
				
		if b in ['    X    ', ' X  OX   ', ' X  O  X ', '   XOX   ', '   XO  X ']:
			return 0
			
		if b in ['X   O   X', '  X O X  ', '   XO   X',
				 '    OXX  ', 'X  OOXX  ', '  XXOO  X',
				 'O  XXO  X']:
			return 1
			
		if b in [' X XO    ', 'O   X   X', '    OX X ']:
			return 2
			
		if b in [' X  O   X', '  X O  X ', 'XOX O  X ',
				 'OX  X  OX', ' X  OXXX ', ' X  O XOX']:
			return 3
		
		if b in ['X        ', ' X       ', '  X      ',
				 '   X     ', '     X   ', '      X  ',
				 '       X ', '        X']:
			return 4
			
		if b in ['X   O  X ', ' X  O X  ']:
			return 5
			
		if b in ['X   OX   ', '  XXO    ']:
			return 7
			
		# The choice doesn't matter, choose one randomly
		return random.choice(self.board.emptySquares())
			
	def highlight(self, *squares):
		for square in squares:
			self.highlighted[square] = True
			
	def unhighlightAll(self):
		self.highlighted = [False for i in range(9)]
			

run(Game(), PORTRAIT)
