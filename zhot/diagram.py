#!/usr/bin/env python3
"""zhot.zhot: provides entry point main()."""

import svgwrite
from matplotlib.mlab import frange
from math import (sqrt, radians, sin, cos)

# Useful functions for all classes in this 
def rounded(num):
	DEC_PLACES = 2
	return round(num, DEC_PLACES)

def dup(single):
	return (single, single)

class Diagram:
	"Class which generates data to output a vector diagram of the game rules."
	FULL_CIRCLE = 360  # degrees
	DIAGRAM_SIZE = 1000

	def __init__(self, move_objs):
		# Import static methods from class
		self.diagram = svgwrite.Drawing(
			filename="diagram.svg",
			size=(self.DIAGRAM_SIZE, self.DIAGRAM_SIZE)
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
			else:  # Otherwise, other angles
				angle_rad = radians(angle % EAST)
				opposite = hypotenuse * sin(angle_rad)
				adjacent = hypotenuse * cos(angle_rad)
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

		# if len(move_points) > len(move_objs):
		# 	print("Slight error: I have data for too many circles in the diagram.")

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
		for i, point in enumerate(move_points):
			the_move_obj = move_objs[i]
			#print(the_move_obj)

			name = "group-%d for %s" % (i, the_move_obj.move)
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
					insert=(downshifted),
					text_anchor="middle",
					textLength=text_length_px,
					lengthAdjust="spacingAndGlyphs",
				)
			)

			# All the various beat lines.
			beats_lines = self.diagram.g(class_="beats")
			for target in move_objs[i].beats_num:
				line = ResizableLine(point, move_points[target]).resize(1 / 3)
				line.resize(1 / 3, from_start=True, from_end=False)
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
		self.dict = dict(x=x, y=y)
		self.tuple = (self.x, self.y) = (x, y)

	def __repr__(self):
		return "Point: " + str(self.dict)

	def __iter__(self):
		return iter(self.tuple)

class ResizableLine:
	"""
		A class storing co-ordinates of a line for later use in, e.g. SVG.
		It provides methods for resizing of the line.
	"""

	def __init__(self, start, end):
		self.start = Point(start)
		self.end = Point(end)
		self._gen_vars()

	def __repr__(self):
		return "Line: " + str(self.dict)

	def __iter__(self):
		return iter(self.tuple)

	def _gen_vars(self):
		"Must be run every time the start or end of the line is modified."
		# Generate some collections.
		self.dict = dict(start=self.start, end=self.end)
		self.tuple = (self.start, self.end) 
		# The base & height of the triangle of the line.
		self.base = self.end.x - self.start.x
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

