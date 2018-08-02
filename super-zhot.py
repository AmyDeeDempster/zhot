#!/usr/bin/env python3
import csv
import random
import sys

def main():
	try:
		game = Game(sys.argv[1])
	except:
		print("Provide a CSV file of possible moves, as a command-line argument.")
		exit()

	# Play the game
	while True:
		round = Round(game)
		print(round.moves, end="")
		print(round.outcome)
		game.score['human'] += round.score['human']
		game.score['ai']    += round.score['ai'] 

	

class Round:
	"""Object that deals with a single round of the game""" 
	def __init__(self, game):
		print("Options: %s." % game.move_names )
		print("What is your move? ", end="")

		# These return instances of Move() or Admin_move()
		human = self.get_human_move(game)
		ai    = random.choice(game.move_objs)
		
		# Check whether that was a real move, or perhaps a move to quit.
		self.moves = str()
		self.outcome = str()
		self.score = dict(human=0, ai=0)
		if human.move:
			self.moves += "You play " + human.move + " and I play " + ai.move + ". "
			if human == ai:
				self.outcome = "Stalemate."
			elif human.move in ai.beats:
				self.outcome = ai.result_vs(human.move)
				self.score['ai'] = 1
			elif ai.move in human.beats:
				self.outcome = human.result_vs(ai.move)
				self.score['human'] = 1
			else:
				raise Exception("Invalid move")
		elif human.quitting:
			print("Exiting.")
			print(game.score)
			exit()

	def get_human_move(self, game):
		stdin = input().strip()
		if not stdin or stdin in ("exit", "quit"):
			return Admin_move(True)
		elif stdin in ("help", "moves", "rules", "?"):
			print(game.rules)
			return Admin_move(False)
		for candidate in game.move_objs:
			if stdin.casefold() in candidate.move.casefold():
				return candidate
		else:
			return Admin_move(False)

class Move:
	"""Object that contains the name of a move,
	   the moves it defeats, and how it defeats them."""
	generic_verb = 'beats'
	def __init__(self, number, total, info, move_names):
		self.move = info.pop(0)
		self.beats = dict()
		# Get a range like [1,3,5]
		for offset in range(1, total, 2):
			# Get a string like "cuts" or "beats".
			try:
				verb = info.pop(0).strip()
			except:
				verb = generic_verb
			# Get a string like "Paper".
			loser = move_names[(number + offset) % total]
			# Set a dictionary entry like {"Paper": "cuts"}
			self.beats[loser] = verb
	def result_vs(self, enemy_move):
		return " ".join((self.move, self.beats[enemy_move], enemy_move)) + "."

class Admin_move:
	"Like Move(), but not concerned with actually playing, but rather stuff like displaying help."
	def __init__(self, quitting):
		self.move = False
		self.quitting = quitting

class Game:
	def __init__(self, filename):
		# Turn CSV into list of strings.
		with open(filename) as filehandle:
			rows = csv.reader(filehandle, delimiter=',', quotechar='"')
			# Ignore blank lines.
			moves = [row for row in rows if len(row)]

		# Turn list of strings into list of Move objects
		move_names = [item[0] for item in moves]
		self.move_objs = list()
		for i, move_info in enumerate(moves):
			new = Move(i, len(moves), move_info, move_names)
			self.move_objs.append(new)

		# Keep score
		self.score = dict(human=0, ai=0)

		# Outside of this class, we'll need this list of moves stringified.
		self.move_names = ", ".join(move_names)

		# Build a string with game rules.
		self.rules = "Rules of the game:\n"
		for obj in self.move_objs:
			for loser, verb in obj.beats.items():
				self.rules += (" ".join((obj.move, verb, loser)) + ".\n")

main()