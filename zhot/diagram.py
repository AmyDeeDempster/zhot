#!/usr/bin/env python3
"""zhot.zhot: provides entry point main()."""

try:
	import svgwrite
except ImportError as e:
	print("""The diagram-generating feature of Zhot will not work unless
the svgwrite package is installed first.  This package is listed
as a dependency of Zhot, but due to a packaging error, this seems not
to be enforced.	""")
from numpy import arange
import os
from math import (sqrt, radians, sin, cos)
import pkg_resources


# Useful functions for all classes in this file.
def rounded(num):
	"""Rounds numbers to a generous number of decimal points,
	since scour will go further if necessary."""
	DEC_PLACES = 4
	return round(num, DEC_PLACES)

def dup(single):
	return (single, single)

class Diagram:
	"Class which generates data to output a vector diagram of the game rules."
	FULL_CIRCLE = 360  # degrees
	DIAGRAM_VB = 1000
	DEF_OUT = "diagram.svg"

	@classmethod
	def create(self, move_objs, size, hue1, hue2, out):
		# Import static methods from class
		if size:
			size = dup(size)
		if not hue1:
			hue1 = "white"
		if not hue2:
			hue2 = "silver"
		if not out:
			out = self.DEF_OUT
		self.diagram = svgwrite.Drawing(
			filename=out,
			size=size
		)

		self.diagram.viewbox(width=self.DIAGRAM_VB, height=self.DIAGRAM_VB)
		angle_slice = Diagram.FULL_CIRCLE / len(move_objs)
		# Get an arange like array([0., 120., 240.])
		angles = arange(0, Diagram.FULL_CIRCLE, angle_slice)
		DIAGRAM_VB_RADIUS = round(self.DIAGRAM_VB / 2)
		CIRCLE_RADIUS = round(DIAGRAM_VB_RADIUS / len(move_objs))
		NORTH, EAST, SOUTH, WEST = (0, 90, 180, 270)
		move_points = list()
		hypotenuse = DIAGRAM_VB_RADIUS - CIRCLE_RADIUS
		for angle in angles:
			# Cardinal points first
			if angle == NORTH or angle == Diagram.FULL_CIRCLE:
				p = Point(DIAGRAM_VB_RADIUS, CIRCLE_RADIUS)
			elif angle == EAST:
				p = Point(self.DIAGRAM_VB - CIRCLE_RADIUS, DIAGRAM_VB_RADIUS)
			elif angle == SOUTH:
				p = Point(DIAGRAM_VB_RADIUS, self.DIAGRAM_VB - CIRCLE_RADIUS)
			elif angle == WEST:
				p = Point(CIRCLE_RADIUS, DIAGRAM_VB_RADIUS)
			else:  # Otherwise, other angles
				angle_rad = radians(angle % EAST)
				opposite = hypotenuse * sin(angle_rad)
				adjacent = hypotenuse * cos(angle_rad)
				if angle < EAST:
					p = Point(DIAGRAM_VB_RADIUS + opposite, DIAGRAM_VB_RADIUS - adjacent)
				elif angle < SOUTH:
					p = Point(DIAGRAM_VB_RADIUS + adjacent, DIAGRAM_VB_RADIUS + opposite)
				elif angle < WEST:
					p = Point(DIAGRAM_VB_RADIUS - opposite, DIAGRAM_VB_RADIUS + adjacent)
				else:
					p = Point(DIAGRAM_VB_RADIUS - adjacent, DIAGRAM_VB_RADIUS - opposite)
			move_points.append(p)
		self.move_points = move_points

		# if len(move_points) > len(move_objs):
		# 	print("Slight error: I have data for too many circles in the diagram.")

		text_size = CIRCLE_RADIUS / 3
		max_text_len = 12


		style = pkg_resources.resource_stream(__name__, "diagram.css")
		style = style.read().decode("utf-8")
		style = style.replace("$TEXTSIZE", str(round(text_size)))
		self.diagram.defs.add(
			self.diagram.style(style)
		)

		gradient = self.diagram.defs.add(
			self.diagram.radialGradient(id="radgrad")
		)
		gradient.add_stop_color('0%', hue1).add_stop_color('100%', hue2)

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
				size=(dup(self.DIAGRAM_VB)),
			)
		)
		decorative.add(
			self.diagram.circle(
				center=(dup(DIAGRAM_VB_RADIUS)),
				r=DIAGRAM_VB_RADIUS,
			)
		)
		self.diagram.add(decorative)

		all_moves_g = self.diagram.g(id="moves")

		# A circle for each move, with legend.
		for i, point in enumerate(move_points):
			the_move_obj = move_objs[i]
			#print(the_move_obj)

			name = "%d-%s" % (i, the_move_obj.move)
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
				line = ResizableLine(
					point, move_points[target]
				).resize(CIRCLE_RADIUS * 2.2, proportional=False)
				# Take a bit more off the end for the arrow.
				line.resize(CIRCLE_RADIUS / 5, proportional=False, from_start=False)
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

		# Now optimise.
		try: 
			from scour import scour
			with open(self.FILE_NAME, "r") as file:
				svg_string = file.read()
				# Remove indentation in stylesheet.
				svg_string = svg_string.replace("\t", "")
				# Optimise with scour.
				options = scour.parse_args([
					"--no-line-breaks",
					"--create-groups",
					"--set-precision=2"
				])
				svg_string = scour.scourString(svg_string, options)
			with open(self.FILE_NAME, "w") as file:
				file.write(svg_string)
		except:
			print("Unable to optimise your diagram with scour.")


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

	def resize(self, chop, proportional=True, from_start=True, from_end=True):
		"""
			Recalculates a new line length, and then (using this as the hypotenuse)
			recalculates the base and height of the triangle of a line.
		"""
		if not proportional: 
			# Pixel value must be converted to a coefficient.
			chop = chop / self.length
		# Divide the resizing between the start and end of the line.		
		if from_start and from_end:
			chop /= 2
		# New base & height.
		base, height = [n * (1 - chop) for n in (self.base, self.height)]
		# Actually calculate the new start/end points.
		start, end = (self.start, self.end)
		if from_start:
			self.start = Point(end.x - base, end.y - height)
		if from_end:
			self.end = Point(start.x + base, start.y + height)
		# Refresh the instance variables. 
		self._gen_vars()
		# We’ve altered the instance in place, but also want to be able to chain.
		return(self)

