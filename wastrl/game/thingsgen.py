import sys
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
			((3, 5), things.ratling),
			((1, 2), things.giant_rat),
			((1, 2), things.rifles),
			((0, 1), things.gatling_gun),
			((0, 1), things.artillery),
			((1, 2), things.missile_of_kaboom),
			((0, 1), things.missile_of_smoke),
			((1, 1), things.device_of_teleport),
			((1, 1), things.device_of_teleport_away),
		],
		city = City(
			things = [
				((1, 2), things.device_of_recuperation),
				((1, 1), things.device_of_major_recuperation),
				((1, 2), things.device_of_teleport),
				((1, 2), things.device_of_teleport_away),
				((0, 1), things.device_of_speed),
				((0, 1), things.device_of_slow),
				((0, 1), things.device_of_petrify),
				((0, 1), things.device_of_mapping),
				((0, 1), things.device_of_desertification),
				((1, 3), things.rifles),
				((1, 2), things.gatling_gun),
				((1, 1), things.artillery),
				((2, 4), things.missile_of_kaboom),
				((1, 2), things.missile_of_smoke),
			],
			guardian = [
				things.megarat,
			]
		)
	),
	Area(
		normal = [
			((3, 5), things.skunk),
			((1, 2), things.dire_skunk),
			((1, 2), things.gatling_gun),
			((0, 1), things.armoured_car),
			((0, 1), things.artillery),
			((0, 1), things.missile_of_kaboom),
			((1, 1), things.missile_of_gas),
			((1, 1), things.device_of_desertification),
			((1, 1), things.device_of_petrify),
		],
		city = City(
			things = [
				((1, 2), things.device_of_recuperation),
				((1, 1), things.device_of_major_recuperation),
				((0, 1), things.device_of_teleport),
				((0, 1), things.device_of_teleport_away),
				((0, 1), things.device_of_speed),
				((0, 1), things.device_of_slow),
				((1, 2), things.device_of_petrify),
				((0, 1), things.device_of_mapping),
				((1, 2), things.device_of_desertification),
				((1, 3), things.gatling_gun),
				((1, 2), things.armoured_car),
				((1, 1), things.artillery),
				((0, 1), things.missile_of_kaboom),
				((1, 2), things.missile_of_gas),
				((0, 1), things.missile_of_smoke),
			],
			guardian = [
				things.super_skunk
			]
		)
	),
	Area(
		normal = [
			((3, 5), things.giant_ant),
			((1, 2), things.fire_ant),
			((1, 2), things.armoured_car),
			((0, 1), things.tank),
			((0, 1), things.artillery),
			((0, 1), things.missile_of_kaboom),
			((1, 1), things.missile_of_fire_bomb),
			((1, 1), things.device_of_teleport),
		],
		city = City(
			things = [
				((1, 2), things.device_of_recuperation),
				((1, 1), things.device_of_major_recuperation),
				((1, 2), things.device_of_teleport),
				((0, 1), things.device_of_teleport_away),
				((0, 1), things.device_of_speed),
				((0, 1), things.device_of_slow),
				((0, 1), things.device_of_petrify),
				((0, 1), things.device_of_mapping),
				((0, 1), things.device_of_desertification),
				((1, 3), things.armoured_car),
				((1, 2), things.tank),
				((1, 1), things.artillery),
				((1, 1), things.saturation_artillery),
				((0, 1), things.missile_of_bigger_kaboom),
				((1, 2), things.missile_of_fire_bomb),
				((0, 1), things.missile_of_smoke),
				((0, 1), things.missile_of_guidedness),
				((0, 1), things.missile_of_cluster_bomb),
			],
			guardian = [
				things.queen_ant
			]
		)
	),
	Area(
		normal = [
			((3, 5), things.mole),
			((1, 2), things.quake_mole),
			((1, 2), things.tank),
			((0, 1), things.ray_gun),
			((1, 3), things.tank),
			((1, 2), things.ray_gun),
			((0, 1), things.saturation_artillery),
			((0, 1), things.artillery),
			((0, 1), things.missile_of_bigger_kaboom),
			((0, 1), things.missile_of_cluster_bomb),
			((1, 1), things.device_of_petrify),
			((1, 1), things.device_of_speed),
		],
		city = City(
			things = [
				((1, 2), things.device_of_recuperation),
				((1, 1), things.device_of_major_recuperation),
				((0, 1), things.device_of_teleport),
				((0, 1), things.device_of_teleport_away),
				((1, 2), things.device_of_speed),
				((0, 1), things.device_of_slow),
				((1, 2), things.device_of_petrify),
				((0, 1), things.device_of_mapping),
				((0, 1), things.device_of_desertification),
				((0, 1), things.device_of_shield),
				((1, 2), things.device_of_tunnellation),
				((1, 1), things.artillery),
				((1, 1), things.saturation_artillery),
				((0, 1), things.missile_of_bigger_kaboom),
				((0, 1), things.missile_of_nuclear_warhead),
				((0, 1), things.missile_of_smoke),
				((0, 1), things.missile_of_guidedness),
			],
			guardian = [
				things.doom_mole
			]
		)
	),
	Area(
		normal = [
			((3, 5), things.laser_bot),
			((1, 3), things.warrior_bot),
			((1, 2), things.ray_gun),
			((0, 1), things.repulsor),
			((0, 1), things.saturation_artillery),
			((0, 1), things.artillery),
			((1, 1), things.missile_of_bigger_kaboom),
			((1, 2), things.missile_of_nuclear_warhead),
			((1, 1), things.device_of_speed),
		],
		city = City(
			things = [
				((1, 2), things.device_of_recuperation),
				((1, 1), things.device_of_major_recuperation),
				((0, 1), things.device_of_teleport),
				((0, 1), things.device_of_teleport_away),
				((1, 2), things.device_of_speed),
				((0, 1), things.device_of_slow),
				((0, 1), things.device_of_petrify),
				((0, 1), things.device_of_mapping),
				((0, 1), things.device_of_desertification),
				((0, 1), things.device_of_shield),
				((1, 3), things.ray_gun),
				((1, 2), things.repulsor),
				((1, 1), things.artillery),
				((1, 1), things.saturation_artillery),
				((0, 1), things.missile_of_bigger_kaboom),
				((0, 1), things.missile_of_smoke),
				((0, 1), things.missile_of_guidedness),
			],
			guardian = [
				things.nuclear_robot
			]
		)
	),
	Area(
		normal = [
			((0, 2), things.giant_rat),
			((0, 2), things.dire_skunk),
			((0, 2), things.fire_ant),
			((0, 2), things.quake_mole),
			((1, 2), things.warrior_bot),
			((1, 1), things.nuclear_robot),
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

def gen_normal(terrain, mountain_spines, city_points, rng, debug_log):
	def gen_for_area(area_i, to_gen, points):
		points = iter(points)
		thing_counts = collections.defaultdict(int)
		for num, maker in to_gen:
			for i in range(num):
				thing = maker()
				utils.spawn(thing, next(points))
				thing_counts[props.name[thing]] += 1
		if debug_log:
			things_str = " ".join(f"{c}x {n}" for n, c in thing_counts.items())
			print(f"normal things in {area_i}: {things_str}", file=sys.stderr)
	to_gen = tuple(tuple((rng.randint(*n), m) for n, m in area_spec.normal) for area_spec in table)
	points = choose_points(to_gen, terrain, mountain_spines, city_points, rng)
	for area_i, (to_gen_for_area, area_points) in enumerate(zip(to_gen, points)):
		gen_for_area(area_i, to_gen_for_area, area_points)

def gen_cities(city_points, mountain_spines, rng, debug_log):
	city_points_in_area = sort_city_points(city_points, mountain_spines)
	for area_i, (city_points, spec) in enumerate(zip(city_points_in_area, table)):
		spec = spec.city
		thing_counts = collections.defaultdict(int)
		guard_counts = collections.defaultdict(int)
		for num, maker in spec.things:
			for _ in range(rng.randint(*num)):
				city_point = city_points[rng.randint(0, len(city_points) - 1)]
				thing = maker()
				utils.spawn(thing, city_point)
				thing_counts[props.name[thing]] += 1
		for city_point in city_points:
			if len(spec.guardian) > 0:
				guardian = spec.guardian[rng.randint(0, len(spec.guardian) - 1)]()
				utils.spawn(guardian, city_point)
				props.is_guarding_city.add(guardian)
				guard_counts[props.name[guardian]] += 1
		if debug_log:
			things_str = " ".join(f"{c}x {n}" for n, c in thing_counts.items())
			print(f"city things in {area_i}: {things_str}", file=sys.stderr)
			guards_str = " ".join(f"{c}x {n}" for n, c in guard_counts.items())
			print(f"city guards in {area_i}: {guards_str}", file=sys.stderr)

def gen(terrain, mountain_spines,city_points, rng, debug_log=False):
	city_points = set(city_points)
	mountain_spines = sorted(mountain_spines, key=lambda s: s[0][0], reverse=True)
	mountain_spines = tuple(tuple(normalize_spine(p)) for p in mountain_spines)
	gen_normal(terrain, mountain_spines, city_points, rng, debug_log=debug_log)
	gen_cities(city_points, mountain_spines, rng, debug_log=debug_log)

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
		things.device_of_teleport,
		things.device_of_super_teleport,
		things.device_of_teleport_away,
		things.device_of_tunnellation,
		things.device_of_mountainization,
		things.device_of_recuperation,
		things.device_of_major_recuperation,
		things.device_of_speed,
		things.device_of_slow,
		things.device_of_petrify,
		things.device_of_desertification,
		things.device_of_mapping,
		things.device_of_shield,
	]
	for make in makers:
		thing = make()
		if thing in props.single_use:
			props.single_use.remove(thing)
		props.is_from_starter_kit.add(thing)
		props.inventory[player].add(thing)
