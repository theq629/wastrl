import heapq

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

def dijkstra(graph, starts, touch, cost=lambda n0, n1: 1):
	fringe = SearchFringe()
	for start in starts:
		fringe.put(start, 0)
	while not fringe.is_empty():
		node = fringe.pop()
		node_dist = fringe.get(node)
		if not touch(node, node_dist):
			break
		for neighbour in graph.neighbours(node):
			new_dist = node_dist + cost(node, neighbour)
			old_dist = fringe.get(neighbour)
			if old_dist is None or new_dist < old_dist:
				fringe.put(neighbour, new_dist)
