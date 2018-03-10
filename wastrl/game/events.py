from .. import data

update = data.Event(False, lambda a, b: a or b, name='update', debug=False)
start_turn = data.Event(name='start_turn')
take_turn = data.Event(name='take_turn')
act = data.Event(None, lambda a, b: b if a is not None else b, name='act')

acted = data.Event(name='acted')
move = data.Event(name='move')
get = data.Event(name='get')
drop = data.Event(name='drop')
die = data.Event(name='die')
win = data.Event(name='win')
lose = data.Event(name='lose')
activate = data.Event(name='activate')
attack = data.Event(name='attack')
take_damage = data.Event(name='take_damage')
examine = data.Event("", lambda a, b: " ".join((a, b)).strip() if b is not None else b, name='examine')
guard_wakeup = data.Event(name='guard_wakeup')
