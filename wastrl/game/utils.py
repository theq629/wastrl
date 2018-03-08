from . import properties as props
from . import events

blocked_cost = float('inf')

def spawn(thing, pos):
	props.position[thing] = pos
	events.move.trigger(thing, None, pos)

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
