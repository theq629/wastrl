import tdl
import tcod, tcod.noise
from ..tdlfixes import heightmaps

def gen(dim, rng):
	noise = tcod.noise.Noise(2, seed=rng)
	height = tcod.heightmap_new(*dim)
	height[:] = 1
	tcod.heightmap_add_fbm(height,
		noise = noise,
		mulx = 6,
		muly = 6,
		addx = 0,
		addy = 0,
		octaves = 5,
		delta = 0,
		scale = 1
	)
	return height
