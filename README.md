Zhot
======

I had some fun teaching myself Perl with my Rock-Paper-Scissors script over at
<https://bitbucket.org/AmyDeeDempster/rock-paper-scissors>

This is a more extensible version in Python, done in a more mathematical
and object-oriented manner.

Usage
------

Supply a Comma-Separated Values file as a command-line argument for this script.
For example:

```zhot moves/moves-5.csv```

In the game, type the name of the move you wish to play.
This can be abbreviated.

Other commands available include:

* `rules` or `help`
* `score`
* `rounds`
* `diagram`
* `exit` or `quit`

You can also just hit Return to quit the game.

Dependencies
------------

* csv
* random
* sys
* math
* svgwrite
* matplotlib.mlab

Interpreter
------------

Python > 3.6

(Tested on macOS and Korora Linux installations of CPython 3.6.5 and 3.7.0b4)

Licence
--------

Creative Commons

See text in LICENCE.html

Further information at <https://creativecommons.org/licences/by-sa/3.0/au/>
