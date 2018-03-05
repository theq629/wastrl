from .. import ui
from .. import game
from . import main_view

def int_pair(s):
	x, y = s.split(',')
	return (int(x), int(y))

if __name__ == '__main__':
	import argparse

	parser = argparse.ArgumentParser(description="Wastrl")
	parser.add_argument('-r', '--resolution', metavar="X,Y",
		dest = "resolution", type = int_pair, default = (80, 50),
		help = "Resolution of display in characters."
	)
	parser.add_argument('-f', '--fullscreen',
		dest = "fullscreen", default = False, action = 'store_true',
		help = "Use fullscreen display."
	)
	parser.add_argument('-s', '--seed',
		dest = "rng_seed", type = int, default = 0,
		help = "Seed for randomness."
	)
	args = parser.parse_args()

	the_game = game.Game(args.rng_seed)

	with ui.Display(screen_dim=args.resolution, fullscreen=args.fullscreen, title="Wastrl") as disp:
		disp.views.add(main_view.MainView(disp, the_game))
