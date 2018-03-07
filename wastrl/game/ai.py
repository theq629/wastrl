from . import events

@events.act.on.handle
def take_player_action(self, thing, available_ap):
	print("AI action", thing.index)
