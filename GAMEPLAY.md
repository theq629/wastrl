Gameplay
========

Action points
-------------

Actions use an action point (AP) system. Your movement range with current AP is shown by the grey radius around you.

Items
-----

Items can be activated (default: a) to use them. Items are in three types:

- Weapons. Except for the basic hand to hand combat weapon, take all your AP to activate.
- Missiles. Are targeted an enemy. Take 1 AP to activate. Single use.
- Devices. Some are targeted at a position, others are not and apply directly to the player. Take 1 AP to activate. Single use.

The range of a targeted item is determined by a movement range and a fire range. The movement range is a pathfinding cost which represents how far you can move the item to activate it. The fire range is a straight-line distance which represents the range of the item itself. When activating this is shown by the two red radius around the player; you can target anywhere in the outer red radius.

In inventory screens items are labelled as follows:

- `[x]` Takes x AP to activate, applies to player.
- `[x y+z]` Takes x AP to activate, has a movement range of y and a fire range of z.
- `(t x-y:r)` Has damage type t, damage amount uniformly distributed in the range [x, y], and radius r.

Cheats / testing
----------------

You can add a `[debug]` section to the config file and set any of the following to `yes`:

- `ignore_fov` Show whole map regardless of FOV.
- `starter_kit` Give the player a set of useful items on startup, with single use limits disabled.

The starter kit includes super shield for effective invulnerability and super teleport for nearly free movement.
