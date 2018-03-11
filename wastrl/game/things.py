from .. import data
from . import properties as props
from .effects import damage as effect_damage
from .effects import explosion as effect_explosion
from .effects import smoke as effect_smoke
from .effects import gas as effect_gas
from .effects import fire as effect_fire
from .effects import desertify as effect_desertify

def Thing(init, *other_inits):
	init = dict(init.items())
	init.update(*other_inits)
	return data.Thing(init)

_creature = {
	props.action_points: 1,
	props.population: 1,
	props.inventory: set(),
	props.is_blocking: True
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

_intrinsic = {
	props.name_article: ""
}

damage_marker = {
	props.name: "explosion",
	props.graphics: props.Graphics(char='+', colour=0xaa0000),
	props.is_visual: True
}

explosion = {
	props.name: "explosion",
	props.graphics: props.Graphics(char='+', colour=0xaa0000),
	props.is_visual: True
}
explosion_smoke = {
	props.name: "explosion smoke",
	props.graphics: props.Graphics(char='+', colour=0xffffff),
	props.is_visual: True,
}

fire = {
	props.name: "fire",
	props.name_article: "some",
	props.graphics: props.Graphics(char='&', colour=0xcc0000),
	props.is_visual: True
}

smoke = {
	props.name: "smoke",
	props.name_article: "some",
	props.graphics: props.Graphics(char='&', colour=0xffffff),
	props.is_visual: True,
	props.blocks_vision: True
}

gas = {
	props.name: "gas",
	props.name_article: "some",
	props.graphics: props.Graphics(char='&', colour=0x999999),
	props.is_visual: True,
	props.blocks_vision: True
}

mountains = Thing({
	props.name: "mountains",
	props.name_article: "",
	props.graphics: props.Graphics(char='^', colour=0xcfc19a),
	props.blocks_vision: True
})
grassland = Thing({
	props.name: "grassland",
	props.name_article: "",
	props.graphics: props.Graphics(char='.', colour=0x10ad80),
	props.walk_over_ap: 1,
	props.is_flamable: True
})
desert = Thing({
	props.name: "desert",
	props.name_article: "",
	props.graphics: props.Graphics(char='.', colour=0xffcf6d),
	props.walk_over_ap: 1
})
forest = Thing({
	props.name: "forest",
	props.name_article: "",
	props.graphics: props.Graphics(char='&', colour=0x345132),
	props.walk_over_ap: 2,
	props.is_flamable: True
})
water = Thing({
	props.name: "water",
	props.name_article: "",
	props.graphics: props.Graphics(char='~', colour=0x22b6f2)
})
road = Thing({
	props.name: "road",
	props.name_article: "",
	props.graphics: props.Graphics(char='.', colour=0x222222),
	props.walk_over_ap: 0.5
})

hand_to_hand = Thing(_intrinsic, {
	props.name: "hand to hand",
	props.activation_target_range: props.ActivationTargetRange(
		move_range = 1,
		fire_range = 0,
	),
	effect_damage.activates_as: effect_damage.Params(
		damage = (5, 5),
		radius = 0
	)
})

teeth = Thing(_intrinsic, {
	props.name: "teeth",
	props.activation_target_range: props.ActivationTargetRange(
		move_range = 1,
		fire_range = 0,
	),
	effect_damage.activates_as: effect_damage.Params(
		damage = (1, 5),
		radius = 0
	)
})

huge_teeth = Thing(_intrinsic, {
	props.name: "huge teeth",
	props.activation_target_range: props.ActivationTargetRange(
		move_range = 1,
		fire_range = 0,
	),
	effect_damage.activates_as: effect_damage.Params(
		damage = (5, 10),
		radius = 1
	)
})

bite = Thing(_intrinsic, {
	props.name: "bite",
	props.activation_target_range: props.ActivationTargetRange(
		move_range = 1,
		fire_range = 0,
	),
	effect_damage.activates_as: effect_damage.Params(
		damage = (3, 10),
		radius = 0
	)
})

fire_attack = Thing(_intrinsic, {
	props.name: "fire attack",
	props.activation_target_range: props.ActivationTargetRange(
		move_range = 0,
		fire_range = 10,
	),
	effect_fire.activates_as: effect_fire.Params(
		radius = 2
	)
})

gas_attack = Thing(_intrinsic, {
	props.name: "gas attack",
	props.activation_target_range: props.ActivationTargetRange(
		move_range = 0,
		fire_range = 10,
	),
	effect_fire.activates_as: effect_fire.Params(
		radius = 2
	)
})

def city():
	return Thing({
		props.name: "city ruin",
		props.graphics: props.Graphics(char='#', colour=0xaaaaaa),
		props.blocks_local_vision: True
	})

def goal():
	return Thing({
		props.name: "Wastrl",
		props.name_article: "",
		props.graphics: props.Graphics(char='#', colour=0xffffff),
		props.is_goal: True
	})

def rifiles():
	return Thing(_weapon, {
		props.name: "rifiles",
		props.name_article: "",
		props.activation_target_range: props.ActivationTargetRange(
			move_range = 10,
			fire_range = 0,
		),
		effect_damage.activates_as: effect_damage.Params(
			damage = (5, 10),
			radius = 1
		)
	})

def gatling_gun():
	return Thing(_weapon, {
		props.name: "gatling gun",
		props.activation_target_range: props.ActivationTargetRange(
			move_range = 10,
			fire_range = 0,
		),
		effect_damage.activates_as: effect_damage.Params(
			damage = (1, 10),
			radius = 2
		)
	})

def armoured_car():
	return Thing(_weapon, {
		props.name: "armoured car",
		props.activation_target_range: props.ActivationTargetRange(
			move_range = 10,
			fire_range = 0,
		),
		effect_explosion.activates_as: effect_explosion.Params(
			damage = (5, 15),
			radius = 1
		)
	})

def tank():
	return Thing(_weapon, {
		props.name: "tank",
		props.activation_target_range: props.ActivationTargetRange(
			move_range = 5,
			fire_range = 1,
		),
		effect_explosion.activates_as: effect_explosion.Params(
			damage = (10, 15),
			radius = 1
		)
	})

def cannon():
	return Thing(_weapon, {
		props.name: "cannon",
		props.activation_target_range: props.ActivationTargetRange(
			move_range = 5,
			fire_range = 5,
		),
		effect_explosion.activates_as: effect_explosion.Params(
			damage = (1, 5),
			radius = 1
		)
	})

def saturation_artillery():
	return Thing(_weapon, {
		props.name: "saturation artillery",
		props.name_article: "",
		props.activation_target_range: props.ActivationTargetRange(
			move_range = 0,
			fire_range = 10,
		),
		effect_explosion.activates_as: effect_explosion.Params(
			damage = (1, 10),
			radius = 4
		)
	})

def artillery():
	return Thing(_weapon, {
		props.name: "artillery",
		props.name_article: "",
		props.activation_target_range: props.ActivationTargetRange(
			move_range = 0,
			fire_range = 15,
		),
		effect_explosion.activates_as: effect_explosion.Params(
			damage = (1, 20),
			radius = 1
		)
	})

def ray_gun():
	return Thing(_weapon, {
		props.name: "ray gun",
		props.activation_target_range: props.ActivationTargetRange(
			move_range = 10,
			fire_range = 0,
		),
		effect_damage.activates_as: effect_damage.Params(
			damage = (10, 20),
			radius = 1
		)
	})

def repulsor():
	return Thing(_weapon, {
		props.name: "repulsor",
		props.activation_target_range: props.ActivationTargetRange(
			move_range = 1,
			fire_range = 0,
		),
		effect_damage.activates_as: effect_damage.Params(
			damage = (10, 30),
			radius = 1
		)
	})

def missile_of_kaboom():
	return Thing(_missile, {
		props.name: "missile of kaboom",
		props.activation_target_range: props.ActivationTargetRange(
			move_range = 0,
			fire_range = 15,
		),
		effect_explosion.activates_as: effect_explosion.Params(
			damage = (5, 20),
			radius = 1
		)
	})

def missile_of_fire_bomb():
	return Thing(_missile, {
		props.name: "missile of fire bomb",
		props.activation_target_range: props.ActivationTargetRange(
			move_range = 0,
			fire_range = 15,
		),
		effect_explosion.activates_as: effect_explosion.Params(
			damage = (10, 25),
			radius = 2
		),
		effect_fire.activates_as: effect_fire.Params(
			radius = 2
		)
	})

def missile_of_nuclear_warhead():
	return Thing(_missile, {
		props.name: "missile of nuclear warhead",
		props.activation_target_range: props.ActivationTargetRange(
			move_range = 0,
			fire_range = 30,
		),
		effect_explosion.activates_as: effect_explosion.Params(
			damage = (50, 100),
			radius = 8
		),
		effect_desertify.activates_as: effect_desertify.Params(
			radius = 5
		)
	})

def missile_of_smoke():
	return Thing(_missile, {
		props.name: "missile of smoke",
		props.activation_target_range: props.ActivationTargetRange(
			move_range = 0,
			fire_range = 15,
		),
		effect_smoke.activates_as: effect_smoke.Params(
			radius = 3
		)
	})

def missile_of_gas():
	return Thing(_missile, {
		props.name: "missile of gas",
		props.activation_target_range: props.ActivationTargetRange(
			move_range = 0,
			fire_range = 15,
		),
		effect_gas.activates_as: effect_gas.Params(
			radius = 3
		)
	})

def device_of_mapping():
	return Thing(_device, {
		props.name: "device of mapping"
	})

def device_of_restoration():
	return Thing(_device, {
		props.name: "device of restoration"
	})

def ratling():
	return Thing(_creature, {
		props.name: "ratling",
		props.graphics: props.Graphics(char='r', colour=0xffffff),
		props.action_points: 10,
		props.population: 10,
		props.inventory: set(),
		props.intrinsics: {
			teeth
		}
	})

def megarat():
	return Thing(_creature, {
		props.name: "megarat",
		props.graphics: props.Graphics(char='R', colour=0xffffff),
		props.action_points: 10,
		props.population: 20,
		props.inventory: set(),
		props.intrinsics: {
			huge_teeth
		}
	})

def giant_ant():
	return Thing(_creature, {
		props.name: "giant ant",
		props.graphics: props.Graphics(char='a', colour=0xbbbbbb),
		props.action_points: 10,
		props.population: 10,
		props.inventory: set(),
		props.intrinsics: {
			bite
		}
	})

def fire_ant():
	return Thing(_creature, {
		props.name: "fire ant",
		props.graphics: props.Graphics(char='a', colour=0xff0000),
		props.action_points: 10,
		props.population: 10,
		props.inventory: set(),
		props.intrinsics: {
			bite,
			fire_attack
		}
	})

def player():
	return Thing(_creature, {
		props.name: "band of people",
		props.graphics: props.Graphics(char='@', colour=0xffffff),
		props.is_player: True,
		props.fov: set(),
		props.seen_fov: set(),
		props.action_points: 5,
		props.population: 100,
		props.inventory: set(),
		props.intrinsics: {
			hand_to_hand
		}
	})
