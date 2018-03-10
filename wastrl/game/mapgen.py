import tdl
import tcod, tcod.noise, tcod.path
from ..tdlfixes import heightmaps
from . import tilemap
from . import things

def rand_point(dim, rng):
	return rng.randint(0, dim[0] - 1), rng.randint(0, dim[1] - 1)

def is_valid_point(dim, point):
	return all(point[i] >= 0 and point[i] < dim[i] for i in range(2))

def clamp_point(dim, point):
	return tuple(max(0, min(dim[i] - 1, point[i])) for i in range(2))

def rand_grouped_blobs(dim, num, pather, rng, min_length, max_length, max_r, min_radius):
	def iter_points():
		for i in range(num):
			length = rng.randint(min_length, max_length)
			start = rand_point(dim, rng)
			end = clamp_point(dim, (start[0] + rng.randint(-length, length), start[1] + rng.randint(-length, length)))
			for x, y in pather.get_path(start[0], start[1], end[0], end[1]):
				dx = rng.randint(-max_r, max_r)
				dy = rng.randint(-max_r, max_r)
				r = rng.randint(min_radius, max(min_radius, max_r - max(abs(dx), abs(dy))))
				p = x + dx, y
				if is_valid_point(dim, p):
					yield p, r
	return tuple(iter_points())

def rand_grouped_spots(dim, num, pather, rng, min_length, max_length, max_r, min_radius, num_per_spine_point):
	def iter_points():
		for i in range(num):
			length = rng.randint(min_length, max_length)
			start = rand_point(dim, rng)
			end = clamp_point(dim, (start[0] + rng.randint(-length, length), start[1] + rng.randint(-length, length)))
			for x, y in pather.get_path(start[0], start[1], end[0], end[1]):
				for j in range(num_per_spine_point):
					dx = rng.randint(-max_r, max_r)
					dy = rng.randint(-max_r, max_r)
					p = x + dx, y + dy
					if is_valid_point(dim, p):
						yield p
	return tuple(iter_points())

def choose_guaranteed_path_points(height, dim, starting_point, ending_point, num_mountain_ranges, rng, max_x_variation=10):
	point_dist = int(dim[0] / (num_mountain_ranges + 1))
	pos_x = int(point_dist / 2)
	yield starting_point
	for i in range(num_mountain_ranges + 1):
		pos_y = rng.randint(0, dim[1] - 1)
		x = pos_x + rng.randint(-max_x_variation, max_x_variation)
		x, _ = clamp_point(dim, (x, pos_y))
		yield x, pos_y
		pos_x += point_dist
	yield ending_point

def make_base_heightmap(dim, noise):
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
	tcod.heightmap_normalize(height, 0.1, 1.5)
	return height

def carve_mountains(height, dim, num_mountain_ranges, pather, rng, max_dist_from_spine=15, min_radius=4, carve_height=4):
	range_dist = int(dim[0] / (num_mountain_ranges + 1))
	spines = []
	for i in range(num_mountain_ranges):
		pos_x = range_dist * (i + 1)
		path = tuple(pather.get_path(pos_x, 0, pos_x, dim[1] - 1))
		spines.append(path)
		j = 0
		while j < len(path):
			x, y = path[j]
			j += rng.randint(1, 5)
			dx = rng.randint(-max_dist_from_spine, max_dist_from_spine)
			r = rng.randint(min_radius, max(min_radius, max_dist_from_spine - abs(dx)))
			if is_valid_point(dim, (x + dx, y)):
				tcod.heightmap_dig_hill(height, x + dx, y, r, carve_height)
	return spines

def carve_lakes(height, dim, num_lakes, pather, rng, min_length=5, max_length=20, max_r=10, min_radius=4, carve_depth=-1):
	def iter_points():
		for (x, y), r in rand_grouped_blobs(dim, num_lakes, pather, rng, min_length, max_length, max_r, min_radius):
			tcod.heightmap_dig_hill(height, x, y, r, carve_depth)
			yield x, y
	return tuple(iter_points())

def smooth(height, dim, rng):
	num_cells = dim[0] * dim[1]
	dx = (-1, -1, -1, 0, 0, 1, 1, 1)
	dy = (-1, 0, 1, -1, 1, -1, 0, 1)
	weight = tuple(1 / 8 for i in range(8))
	tcod.heightmap_kernel_transform(height, 8, dx, dy, weight, 0.0, 100)
	tcod.heightmap_rain_erosion(height, int(num_cells / 10), 1.0, 0.1, rng)

def assign_base_terrain(terrain, height, dim, terrain_info):
	terrain_info = sorted(terrain_info)
	for x in range(dim[0]):
		for y in range(dim[1]):
			h = height[y, x]
			for max_height, terrain_value in terrain_info:
				if h <= max_height:
					terrain[x, y] = terrain_value
					break

def run_rivers(terrain, height, lake_points, dim, num_rivers, rng, max_x_offset):
	blocking = tcod.heightmap_new(*dim)
	tcod.heightmap_copy(height, blocking)
	pather = tcod.path.AStar(blocking, diagonal=100)
	for i in range(num_rivers):
		start = lake_points[rng.randint(0, len(lake_points) - 1)]
		end = clamp_point(dim, (max(0, min(dim[0], start[0] + rng.randint(-max_x_offset, max_x_offset))), rng.randint(0, dim[1] - 1)))
		left_source = False
		for x, y in pather.get_path(start[0], start[1], end[0], end[1]):
			if (terrain[x, y] == things.water and left_source) or terrain[x, y] == things.mountains:
				break
			if terrain[x, y] != things.water:
				left_source = True
			terrain[x, y] = things.water
			tcod.heightmap_dig_hill(blocking, x, y, 4, 100)

def make_walk_map(terrain, height, dim, water_cost=100):
	walkability = tcod.heightmap_new(*dim)
	tcod.heightmap_copy(height, walkability)
	for x in range(dim[0]):
		for y in range(dim[1]):
			if terrain[x, y] == things.water:
				walkability[y, x] = water_cost
	return walkability

def make_guaranteed_paths(terrain, height, dim, starting_point, ending_point, num_guaranteed_paths, num_mountain_ranges, pather, rng, unwalkable_terrains={ things.mountains, things.water }):
	for i in range(num_guaranteed_paths):
		points = iter(choose_guaranteed_path_points(height, dim, starting_point, ending_point, num_mountain_ranges, rng))
		last_point = next(points)
		for point in points:
			path = pather.get_path(last_point[0], last_point[1], point[0], point[1])
			for x, y in path:
				if terrain[x, y] in unwalkable_terrains:
					terrain[x, y] = things.desert
			last_point = point

def make_deserts(terrain, height, dim, num_deserts, pather, rng, min_length=5, max_length=40, max_r=40, min_radius=8):
	template = tcod.heightmap_new(*dim)
	for (x, y), r in rand_grouped_blobs(dim, num_deserts, pather, rng, min_length, max_length, max_r, min_radius):
		tcod.heightmap_dig_hill(template, x, y, r, 10)
	for x in range(dim[0]):
		for y in range(dim[1]):
			h = template[y, x]
			if h > 5 and terrain[x, y] == things.grassland:
				terrain[x, y] = things.desert

def make_forests(terrain, height, dim, num_deserts, pather, rng, min_length=5, max_length=15, max_r=4, min_radius=8):
	for x, y in rand_grouped_spots(dim, num_deserts, pather, rng, min_length, max_length, max_r, min_radius, 50):
		terrain[x, y] = things.forest

def make_cities(terrain, dim, num_cities, rng, x_margin):
	def make():
		for i in range(num_cities):
			p = rng.randint(x_margin, dim[0] - 1), rng.randint(0, dim[1] - 1)
			yield p
			terrain[p] = things.road
	return tuple(make())

def make_roads(terrain, height, city_points, dim, pather, rng, roads_per_city=3, road_change_prob=0.25):
	def draw_road(path):
		drawing = True
		for x, y in path:
			if rng.uniform(0, 1) < road_change_prob:
				drawing = not drawing
			if drawing:
				terrain[x, y] = things.road
			elif terrain[x, y] == things.water:
				terrain[x, y] = things.desert
	for i, src in enumerate(city_points):
		for _ in range(roads_per_city):
			while True:
				j = rng.randint(0, len(city_points) - 1)
				if j != i:
					break
			dst = city_points[j]
		draw_road(pather.get_path(src[0], src[1], dst[0], dst[1]))

default_terrain_info = (
	(0.1, things.water),
	(0.55, things.grassland),
	(100, things.mountains)
)

def gen(rng, dim=(500, 250), num_mountain_ranges=5, num_guaranteed_paths=5, num_lakes=20, num_rivers=20, num_cities=20, num_forests=30, num_deserts=60, terrain_info=default_terrain_info):
	margin = int(dim[1] / 4)
	range_dist = int(dim[0] / (num_mountain_ranges + 1))
	max_point_offset = int(range_dist / 10)
	ending_point = clamp_point(dim, (int(range_dist / 2) + rng.randint(-max_point_offset, max_point_offset), rng.randint(margin, dim[1] - margin)))
	starting_point = clamp_point(dim, (dim[0] - int(range_dist / 2) + rng.randint(-max_point_offset, max_point_offset), rng.randint(margin, dim[1] - margin)))

	noise = tcod.noise.Noise(2, seed=rng)
	height = make_base_heightmap(dim, noise)
	height_pather = tcod.path.AStar(height)
	mountain_spines = carve_mountains(height, dim, num_mountain_ranges, height_pather, rng)
	lake_points = carve_lakes(height, dim, num_mountain_ranges, height_pather, rng)
	height[:] += 1
	smooth(height, dim, rng)

	norm_height = tcod.heightmap_new(*dim)
	tcod.heightmap_copy(height, norm_height)
	tcod.heightmap_normalize(norm_height, 0, 1)

	terrain = tilemap.Tilemap(dim, init=lambda _: things.desert)
	assign_base_terrain(terrain, norm_height, dim, terrain_info)
	make_forests(terrain, height, dim, num_forests, height_pather, rng)
	run_rivers(terrain, height, lake_points, dim, num_rivers, rng, max_x_offset=range_dist)
	walkability = make_walk_map(terrain, height, dim)
	walk_pather = tcod.path.AStar(walkability)
	make_guaranteed_paths(terrain, height, dim, starting_point, ending_point, num_guaranteed_paths, num_mountain_ranges, walk_pather, rng)
	make_deserts(terrain, height, dim, num_deserts, height_pather, rng)
	city_points = make_cities(terrain, dim, num_cities, rng, range_dist)
	city_points += (ending_point,)
	make_roads(terrain, height, city_points, dim, walk_pather, rng)

	return terrain, starting_point, ending_point, city_points, mountain_spines
