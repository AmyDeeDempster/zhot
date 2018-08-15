#!/usr/bin/env python3
import csv
import random
import sys
import math
import svgwrite
from math import (tau, sqrt)
from matplotlib.mlab import frange

def main():
	"An extension to the classic game of Scissors-Paper-Stone, Roshambo, or Zhot."
	try: 
		game = Game(sys.argv[1])
	except IndexError:
		game = DefaultGame()

	# Play the game
	while True:
		the_round = Round(game)
		print(the_round.moves + the_round.outcome)
		game.score.human += the_round.score.human
		game.score.ai    += the_round.score.ai

def rounded(num):
	DEC_PLACES = 2
	return round(num, DEC_PLACES)

class Score:
	"Essentially just a dictionary, but with a custom representation."
	def __init__(self, human=0, ai=0):
		self.human = human
		self.ai    = ai
	def upshot(self):
		if self.ai > self.human:
			return "I win."
		if self.human > self.ai:
			return "You win."
		else:
			return "We have tied."
	def dict(self):
		"Dictionary representation of this class"
		return dict(human=self.human, ai=self.ai)
	def __repr__(self):
		return str(self.dict())
	def __str__(self):
		return "You have scored {} and I have scored {}.".format(
			self.human,
			self.ai
		)

class Round:
	"""Object that deals with a single round of the game"""
	def __init__(self, game):
		print("Options: %s." % game.move_names )
		print("What is your move?", end=" ")

		# These return instances of Move() or AdminMove()
		human = self.get_human_move(game)
		ai    = random.choice(game.move_objs)

		# Check whether that was a real move, or perhaps a move to quit.
		self.moves = str()
		self.outcome = str()
		self.score = Score()
		if human.move:
			self.moves += "You play " + human.move + " and I play " + ai.move + ". "
			if human == ai:
				self.outcome = "Stalemate."
			elif human.move in ai.beats:
				self.outcome = ai.result_vs(human.move)
				self.outcome += " " + random.choice(Move.remarks['victorious'])
				self.score.ai = 1
			elif ai.move in human.beats:
				self.outcome = human.result_vs(ai.move)
				self.outcome += " " + random.choice(Move.remarks['conceding'])
				self.score.human = 1
			else:
				raise Exception("Invalid move")
			self.outcome += "\n"
			game.rounds += 1
		elif human.quitting:
			print("Exiting game.")
			print("{} {} rounds played.".format(game.score, game.rounds))
			print(game.score.upshot())
			exit()

	@staticmethod
	def get_human_move(game):
		"Parse player input."
		stdin = input().strip()
		if not stdin or stdin in ("exit", "quit"):
			return AdminMove(quitting=True)
		elif stdin in ("score", "points"):
			print(game.score)
			return AdminMove(quitting=False)
		elif stdin in ("rounds", "length"):
			print("{} rounds have been played so far.".format(game.rounds))
			return AdminMove(quitting=False)
		elif stdin in ("help", "moves", "rules", "?"):
			print(game.rules)
			return AdminMove(quitting=False)
		elif stdin in ("dia", "diagram"):
			diagram = Diagram(game.move_objs)
			print(diagram.move_points)
			return AdminMove(quitting=True)
		for candidate in game.move_objs:
			if stdin.casefold() in candidate.move.casefold():
				return candidate
		else:
			return AdminMove(quitting=False)

class Move:
	"""Object that contains the name of a move,
	   the moves it defeats, and how it defeats them."""
	remarks = dict(
		victorious=("Heheh.", "The round is mine!", "I win.", "You loser."),
		conceding=("OK.", "Drat!", "You’ve won that one.", "Dammit.", "Argh!")
	)

	generic_verb = 'beats'
	def __init__(self, number, info, move_names):
		self.move = info.pop(0)
		self.beats = dict()
		total = len(move_names)
		# Get a range like [1,3,5]
		for offset in range(1, total, 2):
			# Get a string like "cuts" or "beats".
			try:
				verb = info.pop(0).strip()
			except:
				verb = self.generic_verb
			# Get a string like "Paper".
			loser = move_names[(number + offset) % total]
			# Set a dictionary entry like {"Paper": "cuts"}
			self.beats[loser] = verb
		self.num = number
		self.beats_num = [
			# All the odd-numbered indices (our of all the Move objects),
			# shifted forward by the number of the current move,
			# then made to modulo-wrap, so as to yield e.g. [3, 5, 1]
			(i + number) % total for i in range(total) if i % 2 != 0
		]
	def result_vs(self, enemy_move):
		return " ".join((self.move, self.beats[enemy_move], enemy_move)) + "."
	def __repr__(self):
		string =  "Move name: ‘" + self.move + "’; "
		string += "Move beats: " + str(self.beats) + "; "
		string += "Move num: " + str(self.num) + "; "
		string += "Move beats nums: " + str(self.beats_num) + "; "
		return string

class AdminMove(Move):
	"Like Move(), but not concerned with actually playing, but rather stuff like displaying help."
	def __init__(self, quitting=False):
		self.move = False
		self.quitting = quitting

class NotOddError(ValueError):
	pass

class InsufficientMovesError(ValueError):
	pass

class Game():
	"Object that contains a list of Move objects and strings with info on the game."
	def __init__(self, filename):
		# Turn CSV into list of strings.
		try:
			with open(filename) as filehandle:
				rows = csv.reader(filehandle, delimiter=',', quotechar='"')
				# Ignore blank lines.
				moves_from_file = [row for row in rows if len(row)]
				if len(moves_from_file) % 2 == 0:
					raise NotOddError("For a fair game, there must be an odd number of moves.")
				if len(moves_from_file) < 3:
					raise InsufficientMovesError("Multiple moves are necessary.")
		except UnicodeDecodeError as error:
			print("That is not a valid CSV file.")
			exit()
		except IsADirectoryError:
			print("That’s not a CSV file.  It’s a directory.")
			exit()
		except (FileNotFoundError, NotOddError, InsufficientMovesError) as error:
			print("There has been a problem opening your CSV file.")
			print(error)
			exit()

		# Turn list of strings into list of Move objects
		move_names = [item[0] for item in moves_from_file]
		self.move_objs = list()
		for i, move_info in enumerate(moves_from_file):
			new = Move(i, move_info, move_names)
			self.move_objs.append(new)

		self.complete_initialisation(move_names)
		print("Starting game with rules from {}.".format(filename))

	def complete_initialisation(self, move_names):
		# Keep score
		self.score = Score()
		self.rounds = 0

		# Outside of this class, we'll need this list of moves stringified.
		self.move_names = ", ".join(move_names)

		# Build a string with game rules.
		self.rules = "\nRules of the game:\n"
		for obj in self.move_objs:
			for loser, verb in obj.beats.items():
				self.rules += (" ".join((obj.move, verb, loser)) + ".\n")
		self.rules += "\nMake one of these moves, or use ‘score’, ‘rounds’, ‘help’ or ‘exit’."

class DefaultGame(Game):
	"This is what we use if no game rules are provided."
	def __init__(self):
		move_names = ("Scissors", "Paper", "Rock")
		scissors = Move(0, ["Scissors", "cuts"], move_names)
		paper    = Move(1, ["Paper", "wraps"],   move_names)
		rock     = Move(2, ["Rock", "blunts"],   move_names)
		self.move_objs = [scissors, paper, rock]
		self.complete_initialisation(move_names)
		print("Starting game with default rules.")

class Point:
	def __init__(self, x, y=0):
		# See if the argument is already a Point or collection.
		if type(x) == Point:
			preexisting = x
			x = preexisting.x
			y = preexisting.y
		elif type(x) == tuple or type(x) == list:
			preexisting = x
			x = preexisting[0]
			y = preexisting[1]
		else:
			x, y = (rounded(num) for num in (x, y))
		# Store.
		self.dict  = dict(x=x, y=y)
		self.tuple = (self.x, self.y) = (x, y)
	def __repr__(self):
		return "Point: " + str(self.dict)
	def __iter__(self):
		return iter(self.tuple)

class Diagram:
	"Class which generates data to output a vector diagram of the game rules."
	FULL_CIRCLE = 360 # degrees
	DIAGRAM_SIZE = 1000

	@staticmethod
	def dup(single):
		return (single, single)

	def __init__(self, move_objs):
		# Import static methods from class
		dup = self.dup
		self.diagram = svgwrite.Drawing(
			filename = "diagram.svg",
			size = (self.DIAGRAM_SIZE, self.DIAGRAM_SIZE)
		)
		angle_slice = Diagram.FULL_CIRCLE / len(move_objs)
		# Get a frange like array([0., 120., 240.])
		angles = frange(angle_slice, Diagram.FULL_CIRCLE, angle_slice)
		DIAGRAM_RADIUS = round(self.DIAGRAM_SIZE / 2)
		CIRCLE_RADIUS = round(DIAGRAM_RADIUS / len(move_objs))
		NORTH, EAST, SOUTH, WEST = (0, 90, 180, 270)
		move_points = list()
		hypotenuse = DIAGRAM_RADIUS - CIRCLE_RADIUS
		for angle in angles:
			# Cardinal points first
			if angle == NORTH or angle == Diagram.FULL_CIRCLE:
				p = Point(DIAGRAM_RADIUS, CIRCLE_RADIUS)
			elif angle == EAST:
				p = Point(self.DIAGRAM_SIZE - CIRCLE_RADIUS, DIAGRAM_RADIUS)
			elif angle == SOUTH:
				p = Point(DIAGRAM_RADIUS, self.DIAGRAM_SIZE - CIRCLE_RADIUS)
			elif angle == WEST:
				p = Point(CIRCLE_RADIUS, DIAGRAM_RADIUS)
			else: # Otherwise, other angles
				radians = math.radians(angle % EAST)
				opposite = hypotenuse * math.sin(radians)
				adjacent = hypotenuse * math.cos(radians)
				if angle < EAST:
					p = Point(DIAGRAM_RADIUS + opposite, DIAGRAM_RADIUS - adjacent)
				elif angle < SOUTH:
					p = Point(DIAGRAM_RADIUS + adjacent, DIAGRAM_RADIUS + opposite)
				elif angle < WEST:
					p = Point(DIAGRAM_RADIUS - opposite, DIAGRAM_RADIUS + adjacent)
				else:
					p = Point(DIAGRAM_RADIUS - adjacent, DIAGRAM_RADIUS - opposite)
			move_points.append(p)
		self.move_points = move_points

		if len(move_points) > len(move_objs):
			print("Slight error: I have data for too many circles in the diagram.")

		text_size = CIRCLE_RADIUS / 3
		max_text_len = 12

		# Put as much styling as possible here
		style_sheet = self.diagram.style(
"""
		g#decorative rect {
			stroke-width: 5px;
			stroke: darkGrey;
			fill: silver;
		}
		circle {
			stroke: none;
			fill: url(#radgrad);
		}
		g#moves text {
			font-size: %spx;
		}
		g#moves g line {
			stroke-width: 8px;
			stroke-linecap: round;
			stroke: black;
			marker-end: url(#head);
		}
		marker polygon {
			fill: #500;
		}
""" % round(text_size)
		)
		self.diagram.defs.add(style_sheet)

		gradient = self.diagram.defs.add(
			self.diagram.radialGradient(id="radgrad")
		)
		gradient.add_stop_color('0%', 'white').add_stop_color('100%', 'silver')

		arrowhead = self.diagram.marker(
			insert=(1.5, 2),
			size=(4, 4),
			id="head",
			orient="auto",
		)
		arrowhead.add(
			self.diagram.polygon(
				points=[(0, 0), (4, 2), (0, 4), (1, 2)],
			)
		)

		self.diagram.defs.add(arrowhead)
		# / defs

		decorative = self.diagram.g(id="decorative")
		decorative.add(
			self.diagram.rect(
				insert=(0, 0),
				size=(dup(self.DIAGRAM_SIZE)),
				#fill=gradient.get_paint_server(),
			)
		)
		decorative.add(
			self.diagram.circle(
				center=(dup(DIAGRAM_RADIUS)),
				r=DIAGRAM_RADIUS,
			)
		)
		self.diagram.add(decorative)

		all_moves_g = self.diagram.g(id="moves")

		# A circle for each move, with legend.
		num_moves = len(move_points)
		for i, point in enumerate(move_points):
			the_move_obj = move_objs[i]
			print(the_move_obj)

			name = "for " + the_move_obj.move
			move_group = self.diagram.g(
				id=name.replace(" ", "-"),
			)
			
			move_group.add(
				self.diagram.circle(
					center=(point.tuple),
					r=CIRCLE_RADIUS,
				)
			)

			# Calculate some stuff for the text.
			text = move_objs[i].move
			text_length = max_text_len if (len(text) > max_text_len) else len(text)
			# Turn into coefficient
			text_length /= max_text_len
			# A bit less than double the radius, to allow padding.
			text_length_px = rounded(1.9 * CIRCLE_RADIUS * text_length)
			downshifted = (
				rounded(point.x),
				rounded(point.y + text_size / 4)
			)
			move_group.add(
				self.diagram.text(
					text,
					insert = (downshifted),
					text_anchor = "middle",
					textLength = text_length_px,
					lengthAdjust = "spacingAndGlyphs",
				)
			)

			# All the various beat lines.
			beats_lines = self.diagram.g(id="beats")
			for target in move_objs[i].beats_num:
				line = ResizableLine(point, move_points[target]).resize(1/3)
				line.resize(1/3, from_start=True, from_end=False)
				beats_lines.add(
					self.diagram.line(
						start=line.start,
						end=line.end,
					)
				)
			move_group.add(beats_lines)

			all_moves_g.add(move_group)

		self.diagram.add(all_moves_g)
		self.diagram.save()


class ResizableLine:
	"""
		A class storing co-ordinates of a line for later use in, e.g. SVG.
		It provides methods for resizing of the line.
	"""

	def __init__(self, start, end):
		self.start = Point(start)
		self.end   = Point(end)
		self._gen_vars()
	def __repr__(self):
		return "Line: " + str(self.dict)
	def __iter__(self):
		return iter(self.tuple)

	def _gen_vars(self):
		"Must be run every time the start or end of the line is modified."
		# Generate some collections.
		self.dict   = dict(start=self.start, end=self.end)
		self.tuple  = (self.start, self.end) 
		# The base & height of the triangle of the line.
		self.base   = self.end.x - self.start.x
		self.height = self.end.y - self.start.y
		# Thank you, Pythagorus.
		hypotenuse = sqrt((self.base ** 2) + (self.height ** 2))
		self.length = hypotenuse

	def resize(self, chop, proportional=True, from_start=False, from_end=True):
		"""
			Recalculates a new line length, and then (using this as the hypotenuse)
			recalculates the base and height of the triangle of a line.
		"""
		if not proportional: 
			# Pixel value must be converted to a coefficient.
			chop = chop / self.length
		# Divide the resizing between the start and end of the line.		
		if from_start and from_end:
			chop / 2
		# New base & height.
		base, height = [n * (1 - chop) for n in (self.base, self.height)]
		# Actually calc the new start/end points.
		start, end = (self.start, self.end)
		if from_start:
			self.start = Point(end.x - base, end.y - height)
		if from_end:
			self.end = Point(start.x + base, start.y + height)
		self._gen_vars()
		return(self)

main()
