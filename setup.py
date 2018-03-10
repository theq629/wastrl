from setuptools import setup, find_packages

setup(
	name = "wastrl",
	version = "0.0.1",
	description = "Wastrl seven-day roguelike",
	author = "Max Whitney",
	author_email = "mwhitney@alumni.sfu.ca",
	url = "https://theq629.itch.io/wastrl",
	packages = find_packages(),
	install_requires = [
		'tdl==4.3.0',
		'appdirs==1.4.3'
	],
	entry_points = {
		'gui_scripts': [
			'wastrl = wastrl.client:main'
		]
	},
	package_data = {
		'wastrl': [
			'config/config',
			'config/keys',
			'resources/fonts/*'
		]
	}
)
