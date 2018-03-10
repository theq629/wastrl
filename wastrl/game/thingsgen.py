from . import properties as props
from . import things
from . import utils

table = (
	(
		((5, 5), things.ratling),
	),
	(
		((5, 5), things.fire_ant),
	),
	(
	),
	(
	),
	(
	),
	(
	)
)

def rand_point(dim, rng):
	return rng.randint(0, dim[0] - 1), rng.randint(0, dim[1] - 1)

def normalize_spine(path):
	last_pos = path[0]
	yield last_pos[0]
	yield last_pos
	for pos in path[1:]:
		if pos[1] > last_pos[1]:
			yield pos[0]
		last_pos = pos

def choose_points(to_gen, terrain, mountain_spines, rng):
	mountain_spines = sorted(mountain_spines, key=lambda s: s[0][0], reverse=True)
	mountain_spines = tuple(tuple(normalize_spine(p)) for p in mountain_spines)

	need_points = [sum(n for n, m in area_spec) for area_spec in to_gen]
	total_need_points = sum(need_points)

	points = [[] for _ in need_points]
	while total_need_points > 0:
		point = rand_point(terrain.dim, rng)
		if terrain[point] not in { things.mountains, things.water }:
			for i, spine in enumerate(mountain_spines):
				if point[0] > spine[point[1]]:
					if need_points[i] > 0:
						need_points[i] -= 1
						total_need_points -= 1
						points[i].append(point)
					break

	return points

def gen_for_area(to_gen, points):
	points = iter(points)
	for num, maker in to_gen:
		for i in range(num):
			thing = maker()
			utils.spawn(thing, next(points))

def gen(terrain, mountain_spines, rng):
	to_gen = tuple(tuple((rng.randint(*n), m) for n, m in area_spec) for area_spec in table)
	points = choose_points(to_gen, terrain, mountain_spines, rng)
	for to_gen_for_area, area_points in zip(to_gen, points):
		gen_for_area(to_gen_for_area, area_points)

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
