from . import properties as props
from . import things
from . import utils

def rand_point(dim, rng):
	return rng.randint(0, dim[0] - 1), rng.randint(0, dim[1] - 1)

def gen(terrain, rng, num=100):
	num_done = 0
	while num_done < num:
		point = rand_point(terrain.dim, rng)
		if terrain[point] not in { things.mountains, things.water }:
			npc = utils.spawn(things.ratling(), point)
			num_done += 1
