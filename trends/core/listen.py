import json

from trends.core.client import get_global_client, get_pipe
from trends.core.clock import Clock
from trends.core.listeners import Listener, all_listeners
from trends.core.event import BaseEvent


async def start_all():
	"""
	Call listen on all listeners
	"""
	for listener in all_listeners:
		await _construct(listener)
	
	_backup_clock.start()


async def notify_all(event: BaseEvent):
	"""
	Notify all listeners of event
	"""
	pipe = get_pipe()
	for listener in all_listeners:
		await listener.notify(event, pipe)
	await pipe.execute()


async def save_all():
	"""
	Save the state of all listeners to cache
	"""
	pipe = get_pipe()
	for listener in all_listeners:
		await _save_state(listener, pipe)
	await pipe.execute()


async def stop_all():
	"""
	Kill all listeners. May very well be restarted
	"""
	_backup_clock.stop()
	pipe = get_pipe()
	for listener in all_listeners:
		await _destroy(listener, pipe)
	await pipe.execute()


async def _construct(listener: Listener):
	obj = await get_global_client().get(listener._f.deconstruct_key)
	if obj:
		await listener.construct(json.loads(obj))
		pass
	else:
		await listener.listen()


async def _save_state(listener: Listener, pipe):
	await pipe.set(
		listener._f.deconstruct_key,
		json.dumps(listener.deconstruct())
	)


async def _destroy(listener: Listener, pipe):
	if listener._base:
		listener._base.terminate()
		await _save_state(listener, pipe)
		listener._base = None


BACKUP_INTERVAL = 10

_backup_clock = Clock(save_all, BACKUP_INTERVAL)