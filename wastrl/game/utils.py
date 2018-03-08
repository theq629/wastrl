from . import properties as props
from . import events

blocked_cost = float('inf')

def spawn(thing, pos):
	props.position[thing] = pos
	events.move.trigger(thing, None, pos)
	if thing in props.action_points:
		props.is_alive.add(thing)

def walk_cost(terrain, blocked_cost=blocked_cost):
	def cost(from_pos, pos):
		t = terrain[pos]
		if t not in props.walk_over_ap:
			return blocked_cost
		else:
			return props.walk_over_ap[t]
	return cost

def walk_cost_prop(from_pos, pos):
	try:
		t = props.terrain_at[pos]
	except KeyError:
		return blocked_cost
	if t not in props.walk_over_ap:
		return blocked_cost
	else:
		return props.walk_over_ap[t]

def iter_radius(pos, radius):
	radius_2 = radius**2
	for x in range(pos[0] - radius, pos[0] + radius):
		for y in range(pos[1] - radius, pos[1] + radius):
			d = (pos[0] - x)**2 + (pos[1] - y)**2
			if d < radius_2:
				yield (x, y)
