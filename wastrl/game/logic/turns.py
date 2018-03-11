from ... import data
from .. import properties as props
from .. import events

class TurnManager:
	__slots__ = (
		'_rng',
		'_min_ap',
		'_to_act_this_turn',
		'_taking_turn',
		'_action_this_update'
	)

	def __init__(self, rng, min_ap=1):
		self._rng = rng
		self._min_ap = min_ap
		self._to_act_this_turn = data.OrderedSetProperty()
		self._taking_turn = None
		self._action_this_update = False
		self._start_turn()
		events.act.on.add(self._handle_action)
		events.die.on.add(self._handle_death)

	def update(self, rng):
		event_change = False

		self._action_this_update = False
		if self._taking_turn is None or self._taking_turn not in props.action_points_this_turn or props.action_points_this_turn[self._taking_turn] < self._min_ap:
			if self._taking_turn is not None:
				if self._taking_turn in self._to_act_this_turn:
					self._to_act_this_turn.remove(self._taking_turn)
				self._taking_turn = None
		if len(self._to_act_this_turn) == 0:
			self._start_turn()

		event_change |= events.update.trigger(rng)

		if len(self._to_act_this_turn) > 0:
			next_to_go = next(iter(self._to_act_this_turn))
			if next_to_go != self._taking_turn:
				self._taking_turn = next_to_go
				events.take_turn.trigger(self._taking_turn)

		event_change = event_change
		if self._action_this_update:
			return self._taking_turn, event_change
		else:
			return None, event_change

	def _start_turn(self):
		for thing, ap in props.action_points.items():
			if thing in props.is_player:
				props.action_points_this_turn[thing] = ap
				self._to_act_this_turn.add(thing)
		for thing, ap in props.action_points.items():
			if thing not in props.is_player:
				props.action_points_this_turn[thing] = ap
				self._to_act_this_turn.add(thing)
		events.start_turn.trigger(self._rng)

	def _handle_action(self, actor, action):
		if actor != self._taking_turn:
			print(f"warning: actor {actor} acting out of turn")
		else:
			if action.ap is None or action.ap > props.action_points_this_turn[actor]:
				print(f"warning: actor {actor} requested impossible action")
				events.bad_action.trigger(actor, action)
				if actor not in props.is_player:
					_to_act_this_turn.remove(self._taking_turn)
			else:
				try:
					action.trigger(self._rng)
					if actor in props.action_points_this_turn:
						props.action_points_this_turn[actor] -= action.ap
				except Exception as e:
					print("error in action:", file=sys.stderr)
					traceback.print_exc(file=sys.stderr)
					if actor in _to_act_this_turn:
						_to_act_this_turn.remove(actor)
				events.acted.trigger(actor)
				self._action_this_update = True

	def _handle_death(self, actor):
		if actor in self._to_act_this_turn:
			self._to_act_this_turn.remove(actor)
