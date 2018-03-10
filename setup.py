from distutils.core import setup

setup(
	name = "Wastrl",
	version = "0.0.1",
	description = "Wastrl seven-day roguelike",
	author = "Max Whitney",
	author_email = "mwhitney@alumni.sfu.ca",
	url = "https://theq629.itch.io/wastrl",
	packages = [
		'wastrl'
	],
	entry_points = {
		'gui_scripts': [
			'wastrl = wastrl.client.__main__:main'
		]
	}
)
