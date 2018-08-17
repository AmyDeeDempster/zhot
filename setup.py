#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""setup.py: setuptools control."""

import re
from setuptools import setup


version = re.search(
	'^__version__\s*=\s*"(.*)"',
	open('zhot/zhot.py').read(),
	re.M
	).group(1)

with open("README.rst", "rb") as f:
	long_descr = f.read().decode("utf-8")

setup(
	name = "cmdline-zhot",
	packages = ["zhot"],
	entry_points = {
		"console_scripts": ['zhot = zhot.zhot:main']
		},
	version = version,
	description = "Python command line application bare bones template.",
	long_description = long_descr,
	author = "Amy Dee DEMPSTER",
	author_email = "amy.dempster@student.rmit.edu.au",
	url = "",
	)
