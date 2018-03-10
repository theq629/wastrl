import collections
from . import properties as props
from . import things
from . import utils

Area = collections.namedtuple('Area', (
	'normal',
	'city'
))

City = collections.namedtuple('City', (
	'things',
	'guardian'
))

table = (
	Area(
		normal = [
			((5, 5), things.ratling),
		],
		city = City(
			things = [
				((0, 2), things.missile_of_kaboom),
				((0, 1), things.missile_of_fire_bomb),
				((0, 1), things.cannon),
				((0, 1), things.artillery)
			],
			guardian = [
				things.megarat
			]
		)
	),
	Area(
		normal = [
			((2, 3), things.giant_ant),
			((2, 3), things.fire_ant)
		],
		city = City(
			things = [
			],
			guardian = [
			]
		)
	),
	Area(
		normal = [
		],
		city = City(
			things = [
			],
			guardian = [
			]
		)
	),
	Area(
		normal = [
		],
		city = City(
			things = [
			],
			guardian = [
			]
		)
	),
	Area(
		normal = [
		],
		city = City(
			things = [
			],
			guardian = [
			]
		)
	),
	Area(
		normal = [
		],
		city = City(
			things = [
			],
			guardian = [
			]
		)
	)
)

def rand_point(dim, rng):
	return rng.randint(0, dim[0] - 1), rng.randint(0, dim[1] - 1)

def normalize_spine(path):
	last_pos = path[0]
	yield last_pos[0] # hack since our spines seem to be missing the top most point
	yield last_pos[0]
	for pos in path[1:]:
		if pos[1] > last_pos[1]:
			yield pos[0]
		last_pos = pos

def choose_points(to_gen, terrain, mountain_spines, city_points, rng):
	need_points = [sum(n for n, m in area_spec) for area_spec in to_gen]
	total_need_points = sum(need_points)

	points = [[] for _ in need_points]
	while total_need_points > 0:
		point = rand_point(terrain.dim, rng)
		if terrain[point] not in { things.mountains, things.water } and point not in city_points:
			put_in = -1
			for i, spine in enumerate(mountain_spines):
				if point[0] > spine[point[1]]:
					put_in = i
					break
			if need_points[put_in] > 0:
				need_points[put_in] -= 1
				total_need_points -= 1
				points[put_in].append(point)
	return points

def sort_city_points(city_points, mountain_spines):
	city_points_in_area = [[] for _ in range(len(mountain_spines) + 1)]
	for point in city_points:
		put_in = -1
		for i, spine in enumerate(mountain_spines):
			if point[0] > spine[point[1]]:
				put_in = i
				break
		city_points_in_area[put_in].append(point)
	return city_points_in_area

def gen_normal(terrain, mountain_spines, city_points, rng):
	def gen_for_area(to_gen, points):
		points = iter(points)
		for num, maker in to_gen:
			for i in range(num):
				thing = maker()
				utils.spawn(thing, next(points))
	to_gen = tuple(tuple((rng.randint(*n), m) for n, m in area_spec.normal) for area_spec in table)
	points = choose_points(to_gen, terrain, mountain_spines, city_points, rng)
	for to_gen_for_area, area_points in zip(to_gen, points):
		gen_for_area(to_gen_for_area, area_points)

def gen_cities(city_points, mountain_spines, rng):
	city_points_in_area = sort_city_points(city_points, mountain_spines)
	for city_points, spec in zip(city_points_in_area, table):
		spec = spec.city
		for city_point in city_points:
			for num, maker in spec.things:
				for _ in range(rng.randint(*num)):
					thing = maker()
					utils.spawn(thing, city_point)
			if len(spec.guardian) > 0:
				guardian = spec.guardian[rng.randint(0, len(spec.guardian) - 1)]()
				utils.spawn(guardian, city_point)
				props.is_guarding_city.add(guardian)

def gen(terrain, mountain_spines,city_points, rng):
	city_points = set(city_points)
	mountain_spines = sorted(mountain_spines, key=lambda s: s[0][0], reverse=True)
	mountain_spines = tuple(tuple(normalize_spine(p)) for p in mountain_spines)
	gen_normal(terrain, mountain_spines, city_points, rng)
	gen_cities(city_points, mountain_spines, rng)

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
