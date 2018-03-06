from . import properties as props
from .. import data

mountains = data.Thing({
	props.graphics: props.Graphics(char='^', colour=0xe7e9e8)
})
grassland = data.Thing({
	props.graphics: props.Graphics(char='.', colour=0xcda026),
	props.walk_over_ap: 1
})
desert = data.Thing({
	props.graphics: props.Graphics(char='.', colour=0xcd7c26),
	props.walk_over_ap: 1
})
forest = data.Thing({
	props.graphics: props.Graphics(char='^', colour=0x844400),
	props.walk_over_ap: 2
})
water = data.Thing({
	props.graphics: props.Graphics(char='^', colour=0x22b6f2)
})
road = data.Thing({
	props.graphics: props.Graphics(char='^', colour=0x222222),
	props.walk_over_ap: 0.5
})

def city():
	return data.Thing({
		props.graphics: props.Graphics(char='#', colour=0xaaaaaa)
	})

def goal():
	return data.Thing({
		props.graphics: props.Graphics(char='#', colour=0xffffff),
		props.is_goal: True
	})

def player():
	return data.Thing({
		props.graphics: props.Graphics(char='@', colour=0xffffff),
		props.is_player: True,
		props.action_points: 5
	})
