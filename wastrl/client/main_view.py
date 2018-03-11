import numpy
from .. import ui
from ..ui import basic as basic_ui
from .. import game
from ..game import properties as props
from ..game import events
from ..game import actions
from ..game import tilemap
from ..game import utils as game_utils
from . import commands
from . import texts

keys_for_inventory_menu = tuple("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")

def hex_to_rgb(x):
	if isinstance(x, tuple):
		return x
	else:
		b = x & 0x0000ff
		g = (x & 0x00ff00) >> 8
		r = (x & 0xff0000) >> 16
		return (r, g, b)

class MessageHandler:
	__slots__ = (
		'player',
		'text',
		'changed'
	)

	def __init__(self, player):
		self.player = player
		self.text = ""
		self.changed = False
		events.take_damage.on.add(self.handle_take_damage, priority=100)
		events.die.on.add(self.handle_die, priority=100)
		events.activate.on.add(self.handle_activate, priority=-1)
		events.get.on.add(self.handle_get, priority=100)
		events.drop.on.add(self.handle_drop, priority=100)
		events.guard_wakeup.on.add(self.handle_guard_wakeup, priority=100)

	def message(self, message, *args, **kwargs):
		msg_line = message.format(*args, **kwargs) + "\n"
		self.text += msg_line
		self.changed = True

	def name_thing(self, thing):
		return events.examine.trigger(thing, False)

	def format_list(self, items):
		items = list(items)
		if len(items) == 1:
			return items[0]
		elif len(items) == 2:
			return "{} and {}".format(*items)
		else:
			return ", and ".join((", ".join(items[:-1]), items[-1]))

	def capitalize(self, string):
		return string[0].upper() + string[1:]

	def handle_take_damage(self, target, damage):
		self.message("{target} takes {damage} damage, and has {hp} HP left.", target=self.capitalize(self.name_thing(target)), damage=damage, hp=props.population[target])

	def handle_die(self, actor):
		self.message("{actor} dies.", actor=self.capitalize(self.name_thing(actor)))

	def handle_activate(self, thing, actor, target_pos, _rng):
		self.message("{actor} activate{s} {thing}.", actor=self.capitalize("you" if actor == self.player else self.name_thing(actor)), s="" if actor == self.player else "s", thing=self.name_thing(thing))

	def handle_get(self, actor, thing):
		if actor == self.player:
			self.message("You get {thing}.", thing=self.name_thing(thing))

	def handle_drop(self, actor, thing):
		if actor == self.player:
			self.message("You drop {thing}.", thing=self.name_thing(thing))

	def handle_guard_wakeup(self, actor):
		self.message("Something has awoken in the city ruins. It is {thing}.", thing=self.name_thing(actor))

	def do_look(self, pos):
		things_there = tuple(props.things_at[pos])
		things_there_blocking_local = tuple(t for t in things_there if t in props.blocks_local_vision)
		things = (props.terrain_at[pos],)
		if pos != props.position[self.player] and len(things_there_blocking_local) > 0:
			things += things_there_blocking_local
		else:
			things += things_there
		if len(things) > 0:
			ex_things = tuple(self.name_thing(t) for t in things)
			self.message("You see {things}.", things=self.format_list(ex_things))
		else:
			self.message("You see nothing there.")

class PlayerInterfaceManager:
	__slots__ = (
		'_display',
		'_dialog_keybindings',
		'_inventory_keys',
		'_reserved_things',
		'dialog_max_width'
	)

	def __init__(self, display, dialog_keybindings, dialog_max_width):
		self._display = display
		self._dialog_keybindings = dialog_keybindings
		self._inventory_keys = {}
		self._reserved_things = set()
		self.dialog_max_width = dialog_max_width

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
			max_width = self.dialog_max_width,
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
		return events.examine.trigger(thing, True)

	def keyify_things(self, things):
		return tuple((k, t) for k, t in zip(keys_for_inventory_menu, things))

	def keyify_inventory(self, inventory):
		missing = tuple(t for t in self._inventory_keys if t not in inventory and t not in self._reserved_things)
		for thing in missing:
			del self._inventory_keys[thing]

		for thing in sorted(inventory, key=lambda t: props.name[t] if t in props.name else t):
			if thing not in self._inventory_keys:
				i = None
				for j, key in enumerate(keys_for_inventory_menu):
					if key not in self._inventory_keys.values():
						i = j
						break
				if i is not None:
					self._inventory_keys[thing] = keys_for_inventory_menu[i]

		return sorted((self._inventory_keys[t], t) for t in inventory)

	def reserve_keys(self, things):
		self._reserved_things.update(things)
		self.keyify_inventory(things)


class PlayerController:
	__slots__ = (
		'_player',
		'_game',
		'_event_target',
		'_interface_manager',
		'_message_handler',
		'_map_win',
		'_is_our_turn',
		'_targeting',
		'_finish_targeting_callback'
	)

	def __init__(self, player, game, event_target, interface_manager, message_handler, map_win):
		self._player = player
		self._game = game
		self._event_target = event_target
		self._interface_manager = interface_manager
		self._message_handler = message_handler
		self._map_win = map_win
		self._is_our_turn = False
		self._targeting = False
		self._finish_targeting_callback = None
		events.take_turn.on.add(self.watch_turn)
		self.setup_keys()
		self._interface_manager.reserve_keys(props.intrinsics[self._player])

	def setup_keys(self):
		self._event_target.on_click[commands.move_to_click].add(self.command_move_to_click)
		self._event_target.on_click[commands.mouse_look].add(self.command_mouse_look)
		self._event_target.on_key[commands.look].add(self.command_look)
		self._event_target.on_key[commands.pass_turn].add(self.command_skip)
		self._event_target.on_key[commands.move_n].add(self.command_mover((0, -1)))
		self._event_target.on_key[commands.move_s].add(self.command_mover((0, 1)))
		self._event_target.on_key[commands.move_e].add(self.command_mover((1, 0)))
		self._event_target.on_key[commands.move_w].add(self.command_mover((-1, 0)))
		self._event_target.on_key[commands.move_ne].add(self.command_mover((1, -1)))
		self._event_target.on_key[commands.move_nw].add(self.command_mover((-1, -1)))
		self._event_target.on_key[commands.move_se].add(self.command_mover((1, 1)))
		self._event_target.on_key[commands.move_sw].add(self.command_mover((-1, 1)))
		self._event_target.on_key[commands.inventory].add(self.command_show_inventory)
		self._event_target.on_key[commands.get].add(self.command_get)
		self._event_target.on_key[commands.drop].add(self.command_drop)
		self._event_target.on_key[commands.activate].add(self.command_activate)
		self._event_target.on_key[commands.select_target].add(self.command_select_target)
		self._event_target.on_key[commands.auto_target].add(self.command_auto_target)

	def command_show_inventory(self):
		self._interface_manager.inventory_window(set(props.inventory[self._player]))

	def command_skip(self):
		if self._is_our_turn:
			events.act.trigger(self._player, actions.SkipTurn(self._player))

	def command_get(self):
		if self._is_our_turn:
			things_here = set(t for t in props.things_at[props.position[self._player]] if t != self._player and not t in props.cant_get)
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
			def handle_finish(thing_to_activate, target=None):
				events.act.trigger(self._player, actions.Activate(self._player, thing_to_activate, target))
			def handle_start(thing_to_activate):
				if thing_to_activate in props.activation_target_range:
					move_points, fire_points = self.get_target_range(thing_to_activate)
					self.start_targeting(lambda t: handle_finish(thing_to_activate, t), points=(move_points, fire_points))
				else:
					handle_finish(thing_to_activate)
			activatable = set(props.inventory[self._player]) | set(props.intrinsics[self._player])
			self._interface_manager.activate_window(activatable, handle_start)

	def command_mover(self, delta):
		def handle():
			if self._targeting:
				self._map_win.targeting = tuple(self._map_win.targeting[i] + delta[i] for i in range(2))
			elif self._is_our_turn:
				pos = tuple(props.position[self._player][i] + delta[i] for i in range(2))
				attacked = False
				try:
					if any(t in props.is_blocking for t in props.things_at[pos]) and len(props.intrinsics[self._player]) > 0:
						events.act.trigger(self._player, actions.Activate(self._player, next(iter(props.intrinsics[self._player])), pos))
						attacked = True
				except KeyError:
					pass
				if not attacked:
					events.act.trigger(self._player, actions.Move(self._player, delta))
		return handle

	def command_move_to_click(self, screen_pos):
		win_pos = tuple(screen_pos[i] - self._map_win.pos[i] for i in range(2))
		if all(win_pos[i] >= 0 and win_pos[i] < self._map_win.dim[i] for i in range(2)):
			world_pos = tuple(win_pos[i] + self._map_win.world_offset[i] for i in range(2))
			if self._targeting:
				self._map_win.targeting = world_pos
				self.stop_targeting()
			else:
				path = tilemap.pathfind(
					graph = self._game.terrain,
					starts = (props.position[self._player],),
					goal = world_pos,
					cost = game_utils.walk_cost(self._game.terrain),
					max_dist = props.action_points_this_turn[self._player]
				)
				if path is not None:
					self.move_on_path(path)

	def command_look(self):
		self.start_targeting(self._message_handler.do_look)

	def command_mouse_look(self, screen_pos):
		win_pos = tuple(screen_pos[i] - self._map_win.pos[i] for i in range(2))
		if all(win_pos[i] >= 0 and win_pos[i] < self._map_win.dim[i] for i in range(2)):
			world_pos = tuple(win_pos[i] + self._map_win.world_offset[i] for i in range(2))
			self._message_handler.do_look(world_pos)

	def command_select_target(self):
		self.stop_targeting()

	def command_auto_target(self):
		self._map_win.auto_target()

	def get_target_range(self, thing):
		act_range = props.activation_target_range[thing]
		return game_utils.get_ranges((props.position[self._player],), act_range.move_range, act_range.fire_range)

	def start_targeting(self, callback, points=None):
		self._map_win.start_targeting(points)
		self._targeting = True
		self._finish_targeting_callback = callback

	def stop_targeting(self):
		if self._finish_targeting_callback:
			self._finish_targeting_callback(self._map_win.targeting)
			self._finish_targeting_callback = None
		self._map_win.stop_targeting()
		self._targeting = False

	def move_on_path(self, path):
		path = iter(path)
		pos0 = next(path)
		for pos1 in path:
			delta = tuple(pos1[i] - pos0[i] for i in range(2))
			events.act.trigger(self._player, actions.Move(self._player, delta))
			pos0 = pos1
			self._map_win.redraw()

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
		elif self._player in props.position:
			pos = props.position[self._player]
			self._view_centre = pos
			return pos
		else:
			return self._view_centre

	def stop_free_view(self):
		self._free_view = False

	def view_mover(self, delta, multiplier=10):
		def handler():
			self._free_view = True
			self._view_centre = tuple(self._view_centre[i] + delta[i] * multiplier for i in range(2))
		return handler

class StatusWin(ui.Window):
	__slots__ = (
		'_player',
	)

	def __init__(self, player, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._player = player
		self.on_redraw.add(self.handle_redraw)

	def handle_redraw(self, console):
		bg = 0x222222
		console.clear(bg=bg)
		if self._player in props.is_alive:
			ap = props.action_points_this_turn[self._player]
			ap_str = int(ap) if int(ap) == ap else "%0.2f" % (ap)
			console.draw_str(1, 1, f"AP: {ap_str}", bg=bg)
			console.draw_str(1, 2, f"HP: {props.population[self._player]}", bg=bg)
		else:
			console.draw_str(1, 1, f"DEAD", bg=bg)

class MapWin(ui.Window):
	__slots__ = (
		'_game',
		'_player',
		'_ignore_fov',
		'_player_actions',
		'_view_controller',
		'_free_view',
		'_player_can_move_to',
		'world_offset',
		'targeting',
		'_known_targets',
		'_cur_target_index',
		'_target_move_points',
		'_target_fire_points',
		'_things_map_cache'
	)

	def __init__(self, game, player, ignore_fov=False, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._game = game
		self._player = player
		self._ignore_fov = ignore_fov
		self.on_redraw.add(self.handle_redraw)
		self._player_actions = []
		self._view_controller = ViewController(self._player, self.on_key)
		self._player_can_move_to = set()
		self.world_offset = (0, 0)
		self.targeting = None
		self._known_targets = None
		self._cur_target_index = None
		self._target_move_points = None
		self._target_fire_points = None
		self._things_map_cache = tilemap.Tilemap(game.terrain.dim, init=self.choose_thing_at_pos)
		self.update_can_move_to()
		events.move.on.add(self.watch_moves)
		events.acted.on.add(self.watch_actions)
		events.take_turn.on.add(self.watch_turns)

	def choose_thing_at_pos(self, pos):
		def score_thing(thing):
			if thing in props.is_player:
				return 0
			elif thing in props.is_visual:
				return 1
			elif thing in props.blocks_vision:
				return 2
			elif thing in props.blocks_local_vision:
				return 3
			elif thing in props.is_alive:
				return 4
			else:
				return 5
		try:
			thing = min((t for t in props.things_at[pos] if t in props.graphics), key=score_thing)
		except ValueError:
			thing = None
		return thing

	def update_thing_at_pos(self, pos):
		if pos in props.fov[self._player]:
			self._things_map_cache[pos] = self.choose_thing_at_pos(pos)

	def watch_moves(self, thing, move_from, move_to):
		if move_from is not None:
			self.update_thing_at_pos(move_from)
		if move_to is not None and move_to in props.things_at:
			self.update_thing_at_pos(move_to)
		if thing == self._player:
			self._view_controller.stop_free_view()
			if self._player in props.fov:
				for pos in props.fov[self._player]:
					self._things_map_cache[pos] = self.choose_thing_at_pos(pos)

	def handle_redraw(self, console):
		view_centre = self._view_controller.view_centre
		world_dim = self._game.terrain.dim
		self.world_offset = tuple(view_centre[i] - int(self.dim[i] / 2) for i in range(2))
		screen_bounds = tuple((max(0, -self.world_offset[i]), min(self.dim[i], world_dim[i] - self.world_offset[i])) for i in range(2))
		fov_points = props.fov[self._player]
		seen_points = props.seen_fov[self._player]

		console.clear()

		for screen_x in range(*screen_bounds[0]):
			for screen_y in range(*screen_bounds[1]):
				world_x, world_y = world_pos = self.world_offset[0] + screen_x, self.world_offset[1] + screen_y
				bg = 0x000000
				if self.targeting is not None and world_pos == self.targeting:
					bg = 0xcc0000
				elif self.targeting is not None and world_pos in self._target_move_points:
					bg = 0x440000
				elif self.targeting is not None and world_pos in self._target_fire_points:
					bg = 0x330000
				elif world_pos in self._player_can_move_to:
					bg = 0x111111

				if self._ignore_fov or world_pos in seen_points:
					thing_here = self._things_map_cache[world_pos]
					if thing_here is not None and thing_here in props.graphics:
						graphic = props.graphics[thing_here]
					else:
						graphic = props.graphics[self._game.terrain[world_pos]]

					fg = graphic.colour
					if world_pos not in fov_points:
						fg = hex_to_rgb(fg)
						fg = tuple(int(x * 0.25) for x in fg)

					console.draw_char(screen_x, screen_y, char=graphic.char, fg=fg, bg=bg)

				elif self._target_fire_points is not None and world_pos in self._target_fire_points:
					fg = 0x111111
					console.draw_char(screen_x, screen_y, char='.', fg=fg, bg=bg)

	def is_on_screen(self, world_pos):
		world_x, world_y = world_pos
		screen_x, screen_y = world_x - self.world_offset[0], world_y - self.world_offset[1]
		return screen_x >= 0 and screen_x < self.dim[0] and screen_y >= 0 and screen_y < self.dim[1]

	def start_targeting(self, points=None):
		starting_target = None
		if self._cur_target_index is not None and self._cur_target_index < len(self._known_targets):
			last_targeted = self._known_targets[self._cur_target_index]
			if last_targeted in props.position:
				pos = props.position[last_targeted]
				if (points is None or pos in points[1]) and self.is_on_screen(pos):
					starting_target = last_targeted

		if points is not None:
			move_points, fire_points = points
			self._known_targets = tuple(t for t in props.action_points for p in (props.position[t],) if t != self._player and p in fire_points and self.is_on_screen(p))
			self._target_move_points, self._target_fire_points = points
		else:
			self._known_targets = tuple(t for t in props.action_points for p in (props.position[t],) if t != self._player and self.is_on_screen(p))
			self._target_move_points, self._target_fire_points = set(), set()

		if starting_target is not None and starting_target in self._known_targets:
			self._cur_target_index = self._known_targets.index(starting_target)
			self.targeting = props.position[self._known_targets[self._cur_target_index]]
		else:
			self.targeting = props.position[self._player]

	def stop_targeting(self):
		self.targeting = None
		self._target_move_points = None
		self._target_fire_points = None

	def auto_target(self):
		if self.targeting is not None and len(self._known_targets) > 0:
			if self._cur_target_index is None:
				closest = min(self._known_targets, key=lambda t: sum((props.position[t][i] - props.position[self._player][i])**2 for i in range(2)))
				self._cur_target_index = self._known_targets.index(closest)
			elif self._known_targets is not None:
				self._cur_target_index = (self._cur_target_index + 1) % len(self._known_targets)
			self.targeting = props.position[self._known_targets[self._cur_target_index]]

	def watch_actions(self, actor):
		if actor == self._player:
			self.update_can_move_to()

	def watch_turns(self, actor):
		if actor == self._player:
			self.update_can_move_to()

	def update_can_move_to(self):
		if self._player in props.action_points_this_turn:
			self._player_can_move_to = set()
			cur_ap = props.action_points_this_turn[self._player]
			def touch(pos, dist):
				self._player_can_move_to.add(pos)
				return True
			tilemap.dijkstra(
				graph = self._game.terrain,
				starts = (props.position[self._player],),
				touch = touch,
				cost = game_utils.walk_cost(self._game.terrain),
				max_dist = cur_ap
			)

class MainView(ui.View):
	__slots__ = (
		'_display',
		'_full_keybindings',
		'_game',
		'_player',
		'_bar_width',
		'_dialog_max_width',
		'_status_win',
		'_msg_win',
		'_map_win',
		'_msg_handler'
	)

	def __init__(self, display, full_keybindings, the_game, ignore_fov=False, bar_width=20, dialog_max_width=80, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._display = display
		self._full_keybindings = full_keybindings
		self._game = the_game
		self._player = next(iter(props.is_player))
		self._bar_width = bar_width
		self._dialog_max_width = dialog_max_width
		self._status_win = StatusWin(self._player)
		self._map_win = MapWin(self._game, self._player, ignore_fov=ignore_fov, keybindings=self.keybindings)
		log_colours = basic_ui.default_colours._replace(
			background = 0x222222,
			text = 0x888888
		)
		self._msg_win = basic_ui.TextWindow(text="", title=None, do_keys=None, colours=log_colours)
		self.windows.add(self._status_win)
		self.windows.add(self._map_win)
		self.windows.add(self._msg_win)
		self.on_resize.add(self.resize)
		self.on_frame.add(self.update_game)
		self.on_key[commands.quit].add(self.quit)
		self.on_key[commands.help].add(self.help)
		self._msg_handler = MessageHandler(self._player)
		PlayerController(self._player, self._game, self, PlayerInterfaceManager(display, full_keybindings['dialogs'], dialog_max_width), self._msg_handler, self._map_win)

		events.act.on.add(self.take_player_action)
		events.win.on.add(self.win, priority=100)
		events.lose.on.add(self.lose, priority=100)

	def take_player_action(self, thing, available_ap):
		if thing == self._player:
			actions = tuple(self._map_win._player_actions)
			self._map_win._player_actions.clear()
			return actions
		else:
			return None

	def update_game(self):
		changed = False
		if self._player in props.is_alive:
			changed = self._game.update()
			if self._msg_handler.changed:
				self._msg_win.value = self._msg_handler.text
				self._msg_win.scroll_to_end()
				self._msg_handler.changed = False
				return True
		return changed

	def resize(self, dim):
		status_win_width = min(self._bar_width, dim[0])
		status_win_height = 3
		self._status_win.place((0, 0), (status_win_width, status_win_height))
		self._msg_win.place((0, status_win_height), (status_win_width, dim[1] - status_win_height))
		self._map_win.place((status_win_width, 0), (dim[0] - status_win_width + 1, dim[1]))

	def win(self, player):
		self._display.views.add(basic_ui.ViewWithKeys("You win", texts.win, basic_ui.TextWindow, keybindings=self._full_keybindings['dialogs'], max_width=self._dialog_max_width))
		self.close()

	def lose(self, player):
		self._display.views.add(basic_ui.ViewWithKeys("You lose", texts.lose, basic_ui.TextWindow, keybindings=self._full_keybindings['dialogs'], max_width=self._dialog_max_width))
		self.close()

	def quit(self):
		self._display.views.add(basic_ui.ViewWithKeys(
			title = "Really quit",
			win_maker = lambda *args, **kwargs: basic_ui.MenuWindow(*args, select_handler=self.handle_quit_result, **kwargs),
			keybindings = self._full_keybindings['dialogs'],
			max_width = self._dialog_max_width,
			value = (("y", "Yes"), ("n", "No"))
		))

	def handle_quit_result(self, key):
		if key == "y":
			self._display.views.add(basic_ui.ViewWithKeys("You quit", texts.quit, basic_ui.TextWindow, keybindings=self._full_keybindings['dialogs'], max_width=self._dialog_max_width))
			self.close()

	def help(self):
		key_items = tuple((c, " ".join(ks)) for c, ks in self.keybindings.inverse.items())
		self._display.views.add(basic_ui.ViewWithKeys(
			title = "Help",
			win_maker = basic_ui.MenuWindow,
			keybindings = self._full_keybindings['dialogs'],
			max_width = self._dialog_max_width,
			value = key_items
		))
