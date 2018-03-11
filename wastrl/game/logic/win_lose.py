from .. import properties as props
from .. import events

@events.move.on.handle(1000)
def check_win(actor, move_from, move_to):
	if actor in props.is_player:
		for goal, goal_pos in props.is_goal.join(props.position):
			if goal_pos == move_to:
				events.win.trigger(actor)

@events.die.on.handle(1000)
def check_lose(actor):
	if actor in props.is_player:
		events.lose.trigger(actor)
