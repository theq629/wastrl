class Tilemap:
	__slots__ = (
		'_dim',
		'_storage'
	)

	def __init__(self, dim, init=lambda _: None):
		self._dim = dim
		self._storage = [init((x, y)) for x in range(dim[0]) for y in range(dim[1])]

	def __getitem__(self, pos):
		x, y = pos
		return self._storage[y * self._dim[0] + x]

	def __setitem__(self, pos, value):
		x, y = pos
		self._storage[y * self._dim[0] + x] = value
