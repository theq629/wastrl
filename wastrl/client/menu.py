from . import texts
from .. import ui
from ..ui import basic as basic_ui
from ..game import events

class Menu(ui.View):
	__slots__ = (
		'_display',
		'_full_keybindings',
		'_start_game',
		'_dialog_max_width',
		'_menu_win'
	)

	def __init__(self, display, full_keybindings, start_game, dialog_max_width=80, **kwargs):
		super().__init__(**kwargs)
		self._display = display
		self._full_keybindings = full_keybindings
		self._start_game = start_game
		self._dialog_max_width = dialog_max_width
		self._menu_win = self.make_menu_win()
		self.windows.add(self._menu_win)
		#self.on_frame.add(self.handle_frame) # TODO
		self.on_resize.add(self.resize)

	def make_menu_win(self):
		return basic_ui.MenuWindow(
			title = "Wastrl",
			items = (
				("n", "New game"),
				("s", "New game with seed"),
				("q", "Quit")
			),
			keybindings = self._full_keybindings['dialogs'],
			select_handler = self.handle_menu_choice,
			auto_close_view = False
		)

	def get_seed(self, handle_result):
		view = basic_ui.ViewWithKeys(
			title = "Enter seed",
			value = "",
			win_maker = lambda *args, **kwargs: basic_ui.TextEnterWindow(*args, allow_keys=lambda k: k in "0123456789", **kwargs),
			keybindings = self._full_keybindings['dialogs']
		)
		def finish():
			handle_result(int(view.window.value.strip()))
		view.on_close.add(finish)
		self._display.views.add(view)

	def do_start_game(self):
		pass

	def resize(self, dim):
		main_win_dim_x = dim[0]
		if self._dialog_max_width is not None:
			main_win_dim_x = min(main_win_dim_x, self._dialog_max_width)
		text_width_margin_x = int((dim[0] - main_win_dim_x) / 2)
		self._menu_win.place((text_width_margin_x, 0), (main_win_dim_x, dim[1]))

	def handle_menu_choice(self, choice):
		if choice == 'q':
			self._display.quit()
		elif choice == 'n':
			self._start_game()
			self.close()
		elif choice == 's':
			self.get_seed(lambda s: self._start_game(s))
			self.close()
