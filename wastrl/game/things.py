from . import properties as props
from .. import data

def Thing(init, *other_inits):
	init.update(*other_inits)
	return data.Thing(init)

_creature = {
	props.action_points: 1,
	props.population: 1,
	props.inventory: set()
}

_weapon = {
	props.graphics: props.Graphics(char=')', colour=0xffffff)
}

_missile = {
	props.graphics: props.Graphics(char='/', colour=0xffffff)
}

_device = {
	props.graphics: props.Graphics(char='?', colour=0xffffff)
}

mountains = Thing({
	props.name: "mountains",
	props.graphics: props.Graphics(char='^', colour=0xcfc19a)
})
grassland = Thing({
	props.name: "grassland",
	props.graphics: props.Graphics(char='.', colour=0x10ad80),
	props.walk_over_ap: 1
})
desert = Thing({
	props.name: "desert",
	props.graphics: props.Graphics(char='.', colour=0xffcf6d),
	props.walk_over_ap: 1
})
forest = Thing({
	props.name: "forest",
	props.graphics: props.Graphics(char='&', colour=0x345132),
	props.walk_over_ap: 2
})
water = Thing({
	props.name: "water",
	props.graphics: props.Graphics(char='~', colour=0x22b6f2)
})
road = Thing({
	props.name: "road",
	props.graphics: props.Graphics(char='.', colour=0x222222),
	props.walk_over_ap: 0.5
})

def city():
	return Thing({
		props.name: "city",
		props.graphics: props.Graphics(char='#', colour=0xaaaaaa)
	})

def goal():
	return Thing({
		props.name: "Wastrl",
		props.graphics: props.Graphics(char='#', colour=0xffffff),
		props.is_goal: True
	})

def player():
	return Thing(_creature, {
		props.name: "player",
		props.graphics: props.Graphics(char='@', colour=0xffffff),
		props.is_player: True,
		props.action_points: 5,
		props.population: 100,
		props.inventory: set()
	})

def ratling():
	return Thing(_creature, {
		props.name: "ratling",
		props.graphics: props.Graphics(char='r', colour=0xffffff),
		props.action_points: 3,
		props.population: 10,
		props.inventory: set()
	})

def missile_of_kaboom():
	return Thing(_missile, {
		props.name: "missile of kaboom"
	})

def missile_of_fire_ball():
	return Thing(_missile, {
		props.name: "missile of fire ball"
	})

def missile_of_nuclear_warhead():
	return Thing(_missile, {
		props.name: "missile of nuclear warhead"
	})

def device_of_mapping():
	return Thing(_device, {
		props.name: "device of mapping"
	})

def device_of_restoration():
	return Thing(_device, {
		props.name: "device of restoration"
	})
