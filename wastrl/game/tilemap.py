import heapq

def neighbours(pos):
	x, y = pos
	yield (x - 1, y - 1)
	yield (x - 1, y)
	yield (x - 1, y + 1)
	yield (x, y - 1)
	yield (x, y + 1)
	yield (x + 1, y - 1)
	yield (x + 1, y)
	yield (x + 1, y + 1)

class Tilemap:
	__slots__ = (
		'_dim',
		'_storage'
	)

	def __init__(self, dim, init=lambda _: None):
		self._dim = dim
		self._storage = [init((x, y)) for x in range(dim[0]) for y in range(dim[1])]

	@property
	def dim(self):
		return self._dim

	def __getitem__(self, pos):
		x, y = pos
		return self._storage[y * self._dim[0] + x]

	def __setitem__(self, pos, value):
		x, y = pos
		self._storage[y * self._dim[0] + x] = value

	def fill(self, value):
		for i in range(len(self._storage)):
			self._storage[i] = value

	def neighbours(self, pos):
		x, y = pos
		bound_x, bound_y = self._dim[0] - 1, self.dim[1] - 1
		if x > 0:
			if y > 0:
				yield (x - 1, y - 1)
			yield (x - 1, y)
			if y < bound_y:
				yield (x - 1, y + 1)
		if y > 0:
			yield (x, y - 1)
		if y < bound_y:
			yield (x, y + 1)
		if x < bound_x:
			if y > 0:
				yield (x + 1, y - 1)
			yield (x + 1, y)
			if y < bound_y:
				yield (x + 1, y + 1)

class SearchFringe:
	__slots__ = (
		'_array',
		'_dists'
	)

	def __init__(self):
		self._array = []
		self._dists = {}

	def is_empty(self):
		return len(self._array) == 0

	def put(self, node, dist):
		self._dists[node] = dist
		heapq.heappush(self._array, (dist, node))

	def get(self, node):
		return self._dists.get(node)

	def pop(self):
		return heapq.heappop(self._array)[1]

uniform_cost = lambda n0, n1: 1

def _dijkstra(graph, starts, touch, cost, max_dist=None):
	get_neighbours = neighbours if graph is None else graph.neighbours

	do_touch = touch
	if max_dist is not None:
		def do_touch(node, node_dist):
			if node_dist > max_dist:
				return False
			else:
				return touch(node, node_dist)

	fringe = SearchFringe()
	for start in starts:
		fringe.put(start, 0)
	while not fringe.is_empty():
		node = fringe.pop()
		node_dist = fringe.get(node)
		if not do_touch(node, node_dist):
			break
		for neighbour in get_neighbours(node):
			new_dist = node_dist + cost(node, neighbour)
			old_dist = fringe.get(neighbour)
			if old_dist is None or new_dist < old_dist:
				fringe.put(neighbour, new_dist)
	return fringe

def dijkstra(starts, touch, graph=None, cost=uniform_cost, max_dist=None):
	_dijkstra(graph, starts, touch, cost, max_dist=max_dist)

# TODO: use A*
def pathfind(starts, goal, graph=None, cost=uniform_cost, max_dist=None):
	get_neighbours = neighbours if graph is None else graph.neighbours

	inf = float('inf')
	def dist(node):
		d = fringe.get(node)
		if d is None:
			return inf
		else:
			return d
	def trace_path(node, end):
		node = goal
		while node not in starts:
			yield node
			node = min(get_neighbours(node), key=dist)
		yield node

	found = []
	def touch(node, node_dist):
		if node == goal:
			found.append(node)
			return False
		else:
			return True
	fringe = _dijkstra(graph, starts, touch, cost, max_dist=max_dist)

	if len(found) > 0:
		return reversed(tuple(trace_path(fringe, goal)))
	else:
		return None
