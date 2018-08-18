#!/usr/bin/env python3
"""setup.py: setuptools control."""

import re
from os import listdir
from setuptools import setup


version = re.search(
	r'^__version__\s*=\s*"(.*)"',
	open('zhot/zhot.py').read(),
	re.M
).group(1)

# Find the documentation, no matter the language I wrote it in.
try:
	README = [fn for fn in listdir() if "README" in fn]
	with open(README[0], "rb") as f:
		LONG = f.read().decode("utf-8")
except:
	MESSAGE = "Couldn’t find documentation."
	print(MESSAGE)
	LONG = MESSAGE

setup(
	name = "zhot",
	packages = ["zhot"],
	entry_points = {"console_scripts": ['zhot = zhot.zhot:main']},
	version = version,
	install_requires = [
		'numpy',
		'scour',
		'svgwrite',
	],
	description = "Command-line implementation of Zhot, an extensible Scissors-Paper-Stone game.",
	long_description = LONG,
	author = "Amy Dee DEMPSTER",
	author_email = "amy.dempster@student.rmit.edu.au",
	url = "https://github.com/AmyDeeDempster/zhot",
)
