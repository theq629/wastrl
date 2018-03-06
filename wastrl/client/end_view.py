from . import texts
from .. import ui
from ..ui import basic as basic_ui
from ..game import events

class EndView(ui.View):
	__slots__ = (
		'_display',
		'_game'
	)

	def __init__(self, display, the_game, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._display = display
		self._game = the_game

		events.win.on.add(self.win, priority=100)
		events.lose.on.add(self.lose, priority=100)

	def win(self, player):
		self._display.views.add(basic_ui.TextView("You win", texts.win, keybindings=self.keybindings))
		self.close()

	def lose(self, player):
		self._display.views.add(basic_ui.TextView("You lose", texts.lose, keybindings=self.keybindings))
		self.close()
