from .. import data

take_turn = data.Event()
act = data.Event(None, lambda a, b: b if a is not None else b)

turn = data.Event()
die = data.Event()
win = data.Event()
lose = data.Event()
