#!/usr/bin/env python3
"""zhot.__init__.py: provides means of getting version number."""

import re
from os import (listdir, chdir)

def get_version():
	pattern = r'version-([\d\.]+)'
	try:
		print("This is the current dir:")
		print(listdir())
		print("This is up one:")
		print(listdir('..'))

		try:
			fn = [fn for fn in listdir() if 'README' in fn][0]
		except:
			chdir('..')
			fn = [fn for fn in listdir() if 'README' in fn][0]
		with open(fn, "rb") as fh:
			README_STR = fh.read().decode('utf-8')
		return re.search(pattern, README_STR, re.M).group(1)
	except:
		print('Can’t find version number.')
