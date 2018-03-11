from .. import properties as props
from .. import events

@events.examine.on.handle(0)
def base_examine(thing, detailed):
	if thing not in props.name:
		return ""
	else:
		name = props.name[thing]
		article = None
		if thing in props.name_article:
			article = props.name_article[thing]
		else:
			if len(name) > 0:
				article = "an" if name[0].lower() in "aeiou" else "a"
		if article is not None:
			name = " ".join((article, name))
		return name

@events.examine.on.handle(1)
def examine_activatable(thing, detailed):
	if detailed and thing in props.activation_target_range:
		ap = props.activation_ap[thing] if thing in props.activation_ap else 1
		params = props.activation_target_range[thing]
		return f"[{ap} {params.move_range}+{params.fire_range}]"
