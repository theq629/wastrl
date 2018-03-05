import tcod.random
from . import mapgen

class Game:
	def __init__(self, seed):
		map_dim = 500, 250
		self.rng = tcod.random.Random(tcod.random.MERSENNE_TWISTER, seed=0)
		self.height = mapgen.gen(map_dim, self.rng)
