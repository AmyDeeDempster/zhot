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
		for row in rows:
			# Ignore blank lines.
			if len(row):
				moves.append(row)

	# Turn list of strings into list of Move objects
	move_names = [item[0] for item in moves]
	for i, move_info in enumerate(moves):
		new = Move(i, len(moves), move_info, move_names)
		move_objs.append(new)

	print("Rules of the game:")
	for move in move_objs:
		for loser, verb in move.beats.items():
			print(" ".join((move.move, verb, loser)) + ".")

	# Play the game
	while True:
		human = input().strip()
		if not human:
			print("Exiting.")
			break
		ai = random.choice(move_objs)

		for candidate in move_objs:
			if human.casefold() in candidate.move.casefold():
				human = candidate
				break
		else:
			continue
		
		print("You play " + human.move + " and I play " + ai.move + ".")
		if human == ai:
			print("Stalemate.")
		elif human.move in ai.beats:
			print(ai.result_vs(human.move))
		elif ai.move in human.beats:
			print(human.result_vs(ai.move))
		else:
			print("This code should not be reached.")

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