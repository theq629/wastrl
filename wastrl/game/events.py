from .. import data

take_turn = data.Event()
act = data.Event(None, lambda a, b: b if a is not None else b)

acted = data.Event()
move = data.Event()
get = data.Event()
drop = data.Event()
turn = data.Event()
die = data.Event()
win = data.Event()
lose = data.Event()
activate = data.Event()
