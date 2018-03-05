import tcod

class FixArray:
	def __init__(self, wrapped):
		self._wrapped = wrapped

	@property
	def flags(self):
		return self._wrapped.flags

	@property
	def ctypes(self):
		return self._wrapped.ctypes

	@property
	def dtype(self):
		return self._wrapped.dtype

	@property
	def shape(self):
		y, x = self._wrapped.shape
		return x, y

def heightmap_cdata(array, old=tcod.libtcodpy._heightmap_cdata):
	return old(FixArray(array))

def need_fix():
	try:
		ver = tuple(int(x) for x in tcod.version.__version__.split('.'))
		return ver <= (4, 0, 0)
	except:
		return True

if need_fix():
	tcod.libtcodpy._heightmap_cdata = heightmap_cdata
