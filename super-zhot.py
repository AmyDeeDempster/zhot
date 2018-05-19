#!/usr/bin/env python3
list = [
	('Rock', 'Paper', 'Scissors', 'Spock', 'Lizard'),           # MOVE
	('crushes', 'wraps', 'cuts', 'smashes', 'poisons'),         # BEATS_ADJACENT
	('blunts', 'disproves', 'decapitates', 'vaporises', 'eats') # BEATS_ACROSS
]

def main():
	print('''\
Welcome to the game of 
Rock-Paper-Scissors-Lizard-Spock, 
which is somewhat badly named because
that is not the order of precedence.
Blame The Big Bang Theory.

Type your move.\
''')

main()