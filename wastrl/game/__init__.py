import tcod.random
from . import mapgen

class Game:
	def __init__(self, seed):
		self.rng = tcod.random.Random(tcod.random.MERSENNE_TWISTER, seed=seed)
		self.height, self.terrain = mapgen.gen(self.rng)
