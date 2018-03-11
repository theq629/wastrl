# Wastrl

A roguelike/TBS about getting a band of people across a post-apocalyptic wasteland to reach the haven of Wastrl. For 7DRL 2018.

Mostly an experiment in using traditional roguelike mechanics in more general TBS wargame-like setting.

See `GAMEPLAY.md` for more about gameplay.

## Platforms

Tested on Linux. Should run on OSX and Windows too.

## Running

### Directly

	pip install -r requirements.txt
	python -m wastrl.client

### Installing with pip

	pip install .

And run `wastrl`.

### Building self-contained distribution

	cd distribute
	pip install -r requirements.txt
	./build.sh {version}

Where `{version}` is the version number to use for filenames. This will generate `wastrl-{version}`.tar.gz.

## Config

Copy `wastrl/config/*` to `~/.config/wastrl/` on Linux, or wherever the standard place to put config files is on other platforms.

## Resources

Fonts are from `https://github.com/bhelyer/libtcod-d/tree/master/data/fonts` and are apparently in the public domain.
