intro = """
Your ragged band wanders the wastelands, encountering only mutant monsters and the broken ruins of cities. It is said that in the West there is a city called Wastrl which still survives as a refuge against the horrors.
""".strip()

def make_helpful_intro(keybindings, help_command):
	return """
	{base}

	Press during play for help: {help_keys}
	""".strip().format(
		base = intro,
		help_keys = " ".join(keybindings.inverse[help_command])
	)
	

win = """
You reach Wastrl!
""".strip()

lose = """
Your people all died crossing the wastelands.
""".strip()

quit = """
Your people lay down and gave up. The mutant vultures circle.
""".strip()
