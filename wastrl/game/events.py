from .. import data

act = data.Event(None, lambda a, b: a if a is not None else b)
turn = data.Event()
