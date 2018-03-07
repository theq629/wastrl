from . import properties as props
from .. import data

mountains = data.Thing({
	props.name: "mountains",
	props.graphics: props.Graphics(char='^', colour=0xcfc19a)
})
grassland = data.Thing({
	props.name: "grassland",
	props.graphics: props.Graphics(char='.', colour=0x10ad80),
	props.walk_over_ap: 1
})
desert = data.Thing({
	props.name: "desert",
	props.graphics: props.Graphics(char='.', colour=0xffcf6d),
	props.walk_over_ap: 1
})
forest = data.Thing({
	props.name: "forest",
	props.graphics: props.Graphics(char='&', colour=0x345132),
	props.walk_over_ap: 2
})
water = data.Thing({
	props.name: "water",
	props.graphics: props.Graphics(char='~', colour=0x22b6f2)
})
road = data.Thing({
	props.name: "road",
	props.graphics: props.Graphics(char='.', colour=0x222222),
	props.walk_over_ap: 0.5
})

def city():
	return data.Thing({
		props.name: "city",
		props.graphics: props.Graphics(char='#', colour=0xaaaaaa)
	})

def goal():
	return data.Thing({
		props.name: "Wastrl",
		props.graphics: props.Graphics(char='#', colour=0xffffff),
		props.is_goal: True
	})

def player():
	return data.Thing({
		props.name: "player",
		props.graphics: props.Graphics(char='@', colour=0xffffff),
		props.is_player: True,
		props.action_points: 5,
		props.population: 100,
		props.inventory: set()
	})

def ratling():
	return data.Thing({
		props.name: "ratling",
		props.graphics: props.Graphics(char='r', colour=0xffffff),
		props.action_points: 3,
		props.population: 10,
		props.inventory: set()
	})

def missile_of_kaboom():
	return data.Thing({
		props.name: "missile of kaboom",
		props.graphics: props.Graphics(char=')', colour=0xffffff)
	})

def missile_of_fire_ball():
	return data.Thing({
		props.name: "missile of fire ball",
		props.graphics: props.Graphics(char=')', colour=0xffffff)
	})

def missile_of_nuclear_warhead():
	return data.Thing({
		props.name: "missile of nuclear warhead",
		props.graphics: props.Graphics(char=')', colour=0xffffff)
	})

def device_of_mapping():
	return data.Thing({
		props.name: "device of mapping",
		props.graphics: props.Graphics(char='/', colour=0xffffff)
	})

def device_of_restoration():
	return data.Thing({
		props.name: "device of restoration",
		props.graphics: props.Graphics(char='/', colour=0xffffff)
	})
