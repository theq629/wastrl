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
			((3, 5), things.rifles),
			((1, 3), things.missile_of_kaboom),
			((0, 1), things.gatling_gun),
		],
		city = City(
			things = [
				((1, 1), things.rifles),
				((1, 1), things.gatling_gun),
				((1, 1), things.missile_of_kaboom),
				((0, 1), things.missile_of_bigger_kaboom),
				((0, 1), things.missile_of_smoke),
				((0, 1), things.missile_of_gas),
				((0, 1), things.cannon),
			],
			guardian = [
				things.megarat,
			]
		)
	),
	Area(
		normal = [
			((2, 3), things.giant_ant),
			((2, 3), things.fire_ant),
			((0, 2), things.rifles),
			((3, 5), things.gatling_gun),
			((1, 2), things.armoured_car),
			((1, 2), things.cannon),
			((1, 1), things.missile_of_kaboom),
			((1, 1), things.missile_of_bigger_kaboom),
			((1, 1), things.missile_of_smoke),
			((1, 1), things.missile_of_gas),
		],
		city = City(
			things = [
				((0, 1), things.rifles),
				((0, 1), things.gatling_gun),
				((0, 1), things.armoured_car),
				((0, 1), things.cannon),
				((0, 1), things.tank),
				((0, 1), things.artillery),
				((0, 1), things.saturation_artillery),
				((0, 1), things.missile_of_kaboom),
				((0, 1), things.missile_of_bigger_kaboom),
				((0, 1), things.missile_of_smoke),
				((0, 1), things.missile_of_gas),
			],
			guardian = [
			]
		)
	),
	Area(
		normal = [
			((0, 2), things.rifles),
			((1, 2), things.gatling_gun),
			((3, 5), things.armoured_car),
			((3, 5), things.cannon),
			((1, 2), things.tank),
			((1, 2), things.artillery),
			((0, 1), things.saturation_artillery),
			((0, 1), things.missile_of_kaboom),
			((0, 1), things.missile_of_bigger_kaboom),
			((0, 1), things.missile_of_smoke),
			((0, 1), things.missile_of_gas),
			((1, 2), things.missile_of_fire_bomb),
			((0, 2), things.missile_of_guidedness),
		],
		city = City(
			things = [
				((0, 1), things.rifles),
				((0, 1), things.gatling_gun),
				((0, 1), things.armoured_car),
				((0, 1), things.cannon),
				((0, 1), things.tank),
				((0, 1), things.artillery),
				((0, 1), things.saturation_artillery),
				((0, 1), things.ray_gun),
				((0, 1), things.repulsor),
				((0, 1), things.missile_of_kaboom),
				((0, 1), things.missile_of_bigger_kaboom),
				((0, 1), things.missile_of_smoke),
				((0, 1), things.missile_of_gas),
				((0, 1), things.missile_of_fire_bomb),
				((0, 1), things.missile_of_guidedness),
			],
			guardian = [
			]
		)
	),
	Area(
		normal = [
			((0, 2), things.rifles),
			((1, 2), things.gatling_gun),
			((1, 2), things.armoured_car),
			((1, 2), things.cannon),
			((3, 5), things.tank),
			((3, 5), things.artillery),
			((2, 4), things.saturation_artillery),
			((0, 1), things.ray_gun),
			((0, 1), things.repulsor),
			((0, 1), things.missile_of_kaboom),
			((0, 1), things.missile_of_bigger_kaboom),
			((0, 2), things.missile_of_smoke),
			((0, 2), things.missile_of_gas),
			((0, 2), things.missile_of_fire_bomb),
			((0, 2), things.missile_of_guidedness),
			((1, 2), things.missile_of_fire_bomb),
			((1, 2), things.missile_of_cluster_bomb),
			((0, 1), things.missile_of_nuclear_warhead),
		],
		city = City(
			things = [
				((0, 1), things.rifles),
				((0, 1), things.gatling_gun),
				((0, 1), things.armoured_car),
				((0, 1), things.cannon),
				((0, 1), things.tank),
				((0, 1), things.artillery),
				((0, 1), things.saturation_artillery),
				((1, 1), things.ray_gun),
				((0, 1), things.repulsor),
				((0, 1), things.missile_of_kaboom),
				((0, 1), things.missile_of_bigger_kaboom),
				((0, 1), things.missile_of_smoke),
				((0, 1), things.missile_of_gas),
				((0, 1), things.missile_of_fire_bomb),
				((0, 1), things.missile_of_guidedness),
				((0, 1), things.missile_of_fire_bomb),
				((0, 1), things.missile_of_cluster_bomb),
				((0, 1), things.missile_of_nuclear_warhead),
			],
			guardian = [
			]
		)
	),
	Area(
		normal = [
			((0, 2), things.rifles),
			((1, 2), things.gatling_gun),
			((1, 2), things.armoured_car),
			((1, 2), things.cannon),
			((2, 3), things.tank),
			((2, 3), things.artillery),
			((2, 4), things.saturation_artillery),
			((2, 4), things.ray_gun),
			((2, 4), things.repulsor),
			((0, 1), things.missile_of_kaboom),
			((0, 1), things.missile_of_bigger_kaboom),
			((0, 2), things.missile_of_smoke),
			((0, 2), things.missile_of_gas),
			((0, 2), things.missile_of_fire_bomb),
			((0, 2), things.missile_of_guidedness),
			((0, 2), things.missile_of_fire_bomb),
			((0, 2), things.missile_of_cluster_bomb),
			((1, 3), things.missile_of_nuclear_warhead),
		],
		city = City(
			things = [
				((0, 1), things.rifles),
				((0, 1), things.gatling_gun),
				((0, 1), things.armoured_car),
				((0, 1), things.cannon),
				((0, 1), things.tank),
				((0, 1), things.artillery),
				((0, 1), things.saturation_artillery),
				((0, 1), things.ray_gun),
				((0, 1), things.repulsor),
				((0, 1), things.missile_of_kaboom),
				((0, 1), things.missile_of_bigger_kaboom),
				((0, 1), things.missile_of_smoke),
				((0, 1), things.missile_of_gas),
				((0, 1), things.missile_of_fire_bomb),
				((0, 1), things.missile_of_guidedness),
				((0, 1), things.missile_of_fire_bomb),
				((0, 1), things.missile_of_cluster_bomb),
				((0, 1), things.missile_of_nuclear_warhead),
			],
			guardian = [
			]
		)
	),
	Area(
		normal = [
			((1, 2), things.rifles),
			((1, 2), things.gatling_gun),
			((1, 2), things.armoured_car),
			((1, 2), things.cannon),
			((1, 2), things.tank),
			((1, 2), things.artillery),
			((1, 2), things.saturation_artillery),
			((1, 2), things.ray_gun),
			((1, 2), things.repulsor),
			((0, 1), things.missile_of_kaboom),
			((0, 1), things.missile_of_bigger_kaboom),
			((0, 2), things.missile_of_smoke),
			((0, 2), things.missile_of_gas),
			((0, 2), things.missile_of_fire_bomb),
			((0, 2), things.missile_of_guidedness),
			((0, 2), things.missile_of_fire_bomb),
			((0, 2), things.missile_of_cluster_bomb),
			((1, 3), things.missile_of_nuclear_warhead),
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
		things.rifles,
		things.gatling_gun,
		things.armoured_car,
		things.tank,
		things.cannon,
		things.artillery,
		things.saturation_artillery,
		things.ray_gun,
		things.repulsor,
		things.missile_of_kaboom,
		things.missile_of_bigger_kaboom,
		things.missile_of_cluster_bomb,
		things.missile_of_fire_bomb,
		things.missile_of_guidedness,
		things.missile_of_nuclear_warhead,
		things.missile_of_smoke,
		things.missile_of_gas,
	]
	for make in makers:
		thing = make()
		if thing in props.single_use:
			props.single_use.remove(thing)
		props.is_from_starter_kit.add(thing)
		props.inventory[player].add(thing)
