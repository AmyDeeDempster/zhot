#!/usr/bin/env python3
import csv
import random
import sys

generic_verb = 'beats'

def main():
	try:
		game = Game(sys.argv[1])
	except:
		print("Provide a CSV file of possible moves, as a command-line argument.")
		exit()

	# Play the game
	while True:
		print("Options: %s." % game.move_names )
		print("What is your move? ", end="")

		human = get_human_move(game)
		ai    = random.choice(game.move_objs)
		
		# Check whether that was a real move, or perhaps a move to quit.
		if human.move:
			print("You play", human.move, "and I play", ai.move, end=". ")
			print(round_results(human, ai))
		elif human.quitting:
			break
	print("Exiting.")

def get_human_move(game):
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

def round_results(human, ai):
	if human == ai:
		return "Stalemate."
	elif human.move in ai.beats:
		return ai.result_vs(human.move)
	elif ai.move in human.beats:
		return human.result_vs(ai.move)
	else:
		raise Exception("Invalid move")

class Move:
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

		# Outside of this class, we'll need this list of moves stringified.
		self.move_names = ", ".join(move_names)

		# Build a string with game rules.
		self.rules = "Rules of the game:\n"
		for obj in self.move_objs:
			for loser, verb in obj.beats.items():
				self.rules += (" ".join((obj.move, verb, loser)) + ".\n")

main()