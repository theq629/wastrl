from . import properties as props
from . import things
from . import utils

def rand_point(dim, rng):
	return rng.randint(0, dim[0] - 1), rng.randint(0, dim[1] - 1)

def gen_things(thing_maker, terrain, rng, num):
	num_done = 0
	while num_done < num:
		point = rand_point(terrain.dim, rng)
		if terrain[point] not in { things.mountains, things.water }:
			npc = utils.spawn(thing_maker(), point)
			num_done += 1

def gen(terrain, rng):
	gen_things(things.armoured_car, terrain, rng, 100)
	gen_things(things.tank, terrain, rng, 50)
	gen_things(things.cannon, terrain, rng, 50)
	gen_things(things.artillery, terrain, rng, 50)

	gen_things(things.missile_of_kaboom, terrain, rng, 100)
	gen_things(things.missile_of_fire_bomb, terrain, rng, 50)
	gen_things(things.missile_of_nuclear_warhead, terrain, rng, 10)
	gen_things(things.device_of_mapping, terrain, rng, 50)
	gen_things(things.device_of_restoration, terrain, rng, 50)

	gen_things(things.ratling, terrain, rng, 100)

def set_starting_kit(player):
	makers = [
		things.armoured_car,
		things.tank,
		things.cannon,
		things.artillery,
		things.missile_of_kaboom,
		things.missile_of_fire_bomb,
		things.missile_of_nuclear_warhead,
		things.missile_of_smoke,
		things.device_of_mapping,
		things.device_of_restoration
	]
	for make in makers:
		thing = make()
		props.inventory[player].add(thing)
