#!/usr/bin/env python3
import csv
import random

move_fn = 'moves.csv'
generic_verb = 'beats'


def main():
	move_objs = []
	row_num = 0

	# Turn CSV into list of strings.
	moves = []
	with open(move_fn) as move_fh:
		rows = csv.reader(move_fh, delimiter=',', quotechar='"')
		# Ignore blank lines.
		moves = [row for row in rows if len(row)]

	# Turn list of strings into list of Move objects
	move_names = [item[0] for item in moves]
	for i, move_info in enumerate(moves):
		new = Move(i, len(moves), move_info, move_names)
		move_objs.append(new)
	move_names_str = ", ".join(move_names)

	
	# Play the game
	while True:
		print("Options: %s." % move_names_str )
		print("What is your move? ", end="")

		# Get human player's move.
		stdin = input().strip()

		if not stdin or stdin in ("exit", "quit"):
			print("Exiting.")
			break
		elif stdin in ("help", "moves", "?"):
			rules(move_objs)

		for candidate in move_objs:
			if stdin.casefold() in candidate.move.casefold():
				human = candidate
				break
		else:
			continue

		# Get computer's move.
		ai = random.choice(move_objs)
		
		print("You play", human.move, "and I play", ai.move, end=". ")
		if human == ai:
			print("Stalemate.")
		elif human.move in ai.beats:
			print(ai.result_vs(human.move))
		elif ai.move in human.beats:
			print(human.result_vs(ai.move))
		else:
			print("This code should not be reached.")

def rules(move_objs):
	print("Rules of the game:")
	for move in move_objs:
		for loser, verb in move.beats.items():
			print(" ".join((move.move, verb, loser)) + ".")

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

main()