from . import properties as props
from .. import data

mountains = data.Thing({
	props.graphics: props.Graphics(char='^', colour=0xe7e9e8)
})
grassland = data.Thing({
	props.graphics: props.Graphics(char='.', colour=0xcda026)
})
desert = data.Thing({
	props.graphics: props.Graphics(char='.', colour=0xcd7c26)
})
forest = data.Thing({
	props.graphics: props.Graphics(char='^', colour=0x844400)
})
water = data.Thing({
	props.graphics: props.Graphics(char='^', colour=0x22b6f2)
})
road = data.Thing({
	props.graphics: props.Graphics(char='^', colour=0x222222)
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
		props.action_points: 5
	})
