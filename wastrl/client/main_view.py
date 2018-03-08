import numpy
from .. import ui
from ..ui import basic as basic_ui
from .. import game
from ..game import properties as props
from ..game import events
from ..game import actions
from ..game import tilemap
from . import commands

keys_for_inventory_menu = tuple("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")

class PlayerInterfaceManager:
	__slots__ = (
		'_display',
		'_dialog_keybindings',
		'_inventory_keys'
	)

	def __init__(self, display, dialog_keybindings):
		self._display = display
		self._dialog_keybindings = dialog_keybindings
		self._inventory_keys = {}

	def menu(self, items=(), name_value=lambda x: x, select_handler=None, select_multi=False, **kwargs):
		named_items = [(k, name_value(v)) for k, v in items]
		if select_handler is None:
			handle = None
		elif select_multi:
			def handle(selected_keys):
				select_handler(tuple(v for k, v in items if k in selected_keys))
		else:
			def handle(selected_key):
				for key, value in items:
					if key == selected_key:
						select_handler(value)
						return
		self._display.views.add(basic_ui.ViewWithKeys(
			win_maker = lambda *args, **kwargs: basic_ui.MenuWindow(*args, select_handler=handle, select_multi=select_multi, **kwargs),
			keybindings = self._dialog_keybindings,
			max_width = 80,
			value = named_items,
			**kwargs
		))

	def inventory_window(self, inventory):
		self.menu(
			title = "Inventory",
			items = self.keyify_inventory(inventory),
			name_value = self.name_for_thing
		)

	def drop_window(self, inventory, handler):
		self.menu(
			title = "Drop",
			items = self.keyify_inventory(inventory),
			name_value = self.name_for_thing,
			select_handler = handler,
			select_multi = True
		)

	def get_window(self, things, handler):
		self.menu(
			title = "Get",
			items = self.keyify_things(things),
			name_value = self.name_for_thing,
			select_handler = handler,
			select_multi = True
		)

	def activate_window(self, inventory, handler):
		self.menu(
			title = "Activate",
			items = self.keyify_inventory(inventory),
			name_value = self.name_for_thing,
			select_handler = handler,
			select_multi = False
		)

	def name_for_thing(self, thing):
		if thing in props.name:
			return props.name[thing]
		else:
			return "<unknown>"

	def keyify_things(self, things):
		return tuple((k, t) for k, t in zip(keys_for_inventory_menu, things))

	def keyify_inventory(self, inventory):
		for thing in self._inventory_keys:
			if thing not in inventory:
				del self._inventory_keys[thing]

		for thing in inventory:
			if thing not in self._inventory_keys:
				i = None
				for j, key in enumerate(keys_for_inventory_menu):
					if key not in self._inventory_keys.values():
						i = j
						break
				if i is not None:
					self._inventory_keys[thing] = keys_for_inventory_menu[i]

		return sorted((self._inventory_keys[t], t) for t in inventory)

class PlayerController:
	__slots__ = (
		'_player',
		'_on_key',
		'_interface_manager',
		'_is_our_turn'
	)

	def __init__(self, player, on_key, interface_manager):
		self._player = player
		self._on_key = on_key
		self._interface_manager = interface_manager
		self._is_our_turn = False
		events.take_turn.on.add(self.watch_turn)
		self.setup_keys()

	def setup_keys(self):
		self._on_key[commands.pass_turn].add(self.command_skip)
		self._on_key[commands.move_n].add(self.command_mover((0, -1)))
		self._on_key[commands.move_s].add(self.command_mover((0, 1)))
		self._on_key[commands.move_e].add(self.command_mover((1, 0)))
		self._on_key[commands.move_w].add(self.command_mover((-1, 0)))
		self._on_key[commands.move_ne].add(self.command_mover((1, -1)))
		self._on_key[commands.move_nw].add(self.command_mover((-1, -1)))
		self._on_key[commands.move_se].add(self.command_mover((1, 1)))
		self._on_key[commands.move_sw].add(self.command_mover((-1, 1)))
		self._on_key[commands.inventory].add(self.command_show_inventory)
		self._on_key[commands.get].add(self.command_get)
		self._on_key[commands.drop].add(self.command_drop)
		self._on_key[commands.activate].add(self.command_activate)

	def command_show_inventory(self):
		self._interface_manager.inventory_window(set(props.inventory[self._player]))

	def command_skip(self):
		if self._is_our_turn:
			events.act.trigger(self._player, actions.SkipTurn(self._player))

	def command_get(self):
		if self._is_our_turn:
			things_here = set(t for t in props.things_at[props.position[self._player]] if t != self._player)
			def handle(things_to_get):
				events.act.trigger(self._player, actions.Get(self._player, things_to_get))
			self._interface_manager.get_window(things_here, handle)

	def command_drop(self):
		if self._is_our_turn:
			def handle(things_to_drop):
				events.act.trigger(self._player, actions.Drop(self._player, things_to_drop))
			self._interface_manager.drop_window(set(props.inventory[self._player]), handle)

	def command_activate(self):
		if self._is_our_turn:
			def handle(thing_to_activate):
				print("user wants to activate", thing_to_activate.index)
			self._interface_manager.activate_window(set(props.inventory[self._player]), handle)

	def command_mover(self, delta):
		def handle():
			if self._is_our_turn:
				events.act.trigger(self._player, actions.Move(self._player, delta))
		return handle

	def watch_turn(self, actor):
		self._is_our_turn = actor == self._player

class ViewController:
	__slots__ = (
		'_player',
		'_on_key',
		'_view_centre',
		'_free_view'
	)

	def __init__(self, player, on_key):
		self._player = player
		self._on_key = on_key
		self._free_view = False
		self.view_centre
		self.setup_keys()

	def setup_keys(self):
		self._on_key[commands.centre_view].add(self.stop_free_view)
		self._on_key[commands.move_view_n].add(self.view_mover((0, -1)))
		self._on_key[commands.move_view_s].add(self.view_mover((0, 1)))
		self._on_key[commands.move_view_e].add(self.view_mover((1, 0)))
		self._on_key[commands.move_view_w].add(self.view_mover((-1, 0)))
		self._on_key[commands.move_view_ne].add(self.view_mover((1, -1)))
		self._on_key[commands.move_view_nw].add(self.view_mover((-1, -1)))
		self._on_key[commands.move_view_se].add(self.view_mover((1, 1)))
		self._on_key[commands.move_view_sw].add(self.view_mover((-1, 1)))

	@property
	def view_centre(self):
		if self._free_view:
			return self._view_centre
		else:
			pos = props.position[self._player]
			self._view_centre = pos
			return pos

	def stop_free_view(self):
		self._free_view = False

	def view_mover(self, delta, multiplier=10):
		def handler():
			self._free_view = True
			self._view_centre = tuple(self._view_centre[i] + delta[i] * multiplier for i in range(2))
		return handler

class TopBarWin(ui.Window):
	__slots__ = (
		'_player',
	)

	def __init__(self, player, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._player = player
		self.on_redraw.add(self.redraw)

	def redraw(self, console):
		ap = props.action_points_this_turn[self._player]
		ap_str = int(ap) if int(ap) == ap else "%0.2f" % (ap)
		console.clear()
		console.draw_str(0, 0, f'AP: {ap_str} Pop: {props.population[self._player]}')

class MapWin(ui.Window):
	__slots__ = (
		'_game',
		'_player',
		'_player_actions',
		'_view_controller',
		'_free_view',
		'_player_can_move_to'
	)

	def __init__(self, game, player, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._game = game
		self._player = player
		self.on_redraw.add(self.redraw)
		self._player_actions = []
		self._view_controller = ViewController(self._player, self.on_key)
		self._player_can_move_to = set()
		self.update_can_move_to()
		events.move.on.add(self.watch_move)
		events.acted.on.add(self.watch_actions)

	def watch_move(self, actor, move_from, move_to):
		if actor == self._player:
			self._view_controller.stop_free_view()

	def redraw(self, console):
		view_centre = self._view_controller.view_centre
		world_dim = self._game.terrain.dim
		world_offset = tuple(view_centre[i] - int(self.dim[i] / 2) for i in range(2))
		screen_bounds = tuple((max(0, -world_offset[i]), min(self.dim[i], world_dim[i] - world_offset[i])) for i in range(2))

		console.clear()

		for screen_x in range(*screen_bounds[0]):
			for screen_y in range(*screen_bounds[1]):
				world_x, world_y = world_offset[0] + screen_x, world_offset[1] + screen_y
				terrain = self._game.terrain[world_x, world_y]
				graphic = props.graphics[terrain]
				bg = 0x000000
				if (world_x, world_y) in self._player_can_move_to:
					bg = 0x111111
				console.draw_char(screen_x, screen_y, char=graphic.char, fg=graphic.colour, bg=bg)

		# TODO: cache
		for thing, graphic, (world_x, world_y) in props.graphics.join_keys(props.position):
			screen_x, screen_y = world_x - world_offset[0], world_y - world_offset[1]
			if screen_x >= 0 and screen_x < self.dim[0] and screen_y >= 0 and screen_y < self.dim[1]:
				console.draw_char(screen_x, screen_y, char=graphic.char, fg=graphic.colour)

	def watch_actions(self, actor):
		if actor == self._player:
			self.update_can_move_to()

	def update_can_move_to(self):
		self._player_can_move_to = set()
		cur_ap = props.action_points_this_turn[self._player]
		def touch(pos, dist):
			if dist <= cur_ap:
				self._player_can_move_to.add(pos)
				return True
			else:
				return False
		tilemap.dijkstra(
			graph = self._game.terrain,
			starts = (props.position[self._player],),
			touch = touch,
			cost = lambda _, p: props.walk_over_ap[self._game.terrain[p]]
		)

class MainView(ui.View):
	__slots__ = (
		'_display',
		'_full_keybindings',
		'_game',
		'_player',
		'_top_bar_win',
		'_map_win'
	)

	def __init__(self, display, full_keybindings, the_game, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._display = display
		self._full_keybindings = full_keybindings
		self._game = the_game
		self._player = next(iter(props.is_player))
		self._top_bar_win = TopBarWin(self._player)
		self._map_win = MapWin(self._game, self._player, keybindings=self.keybindings)
		self.windows.add(self._top_bar_win)
		self.windows.add(self._map_win)
		self.on_resize.add(self.resize)
		self.on_frame.add(self.update_game)
		events.act.on.add(self.take_player_action)
		events.win.on.add(self.win_or_lose, priority=99)
		events.lose.on.add(self.win_or_lose, priority=99)
		self.on_key[commands.quit].add(self._display.quit)
		PlayerController(self._player, self.on_key, PlayerInterfaceManager(display, full_keybindings['dialogs']))

	def take_player_action(self, thing, available_ap):
		if thing == self._player:
			actions = tuple(self._map_win._player_actions)
			self._map_win._player_actions.clear()
			return actions
		else:
			return None

	def win_or_lose(self, player):
		self.close()

	def update_game(self):
		return self._game.update()

	def resize(self, dim):
		self._top_bar_win.place((0, 0), (dim[0], 1))
		self._map_win.place((0, 1), (dim[0], dim[1] - 1))
