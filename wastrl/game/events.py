from .. import data

update = data.Event(False, lambda a, b: a or b)
start_turn = data.Event()
take_turn = data.Event()
act = data.Event(None, lambda a, b: b if a is not None else b)

acted = data.Event()
move = data.Event()
get = data.Event()
drop = data.Event()
die = data.Event()
win = data.Event()
lose = data.Event()
activate = data.Event()
attack = data.Event()
take_damage = data.Event()
examine = data.Event("", lambda a, b: " ".join((a, b)).strip() if b is not None else b)
