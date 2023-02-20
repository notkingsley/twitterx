from typing import Type

from feeds.core.client import get_pipe
from feeds.core.event import BaseEvent
from feeds.core.formulas import (
	BaseFormula,
	KeywordTrendFormula,
	KeywordVolumeFormula,
	TagTrendFormula,
	TagVolumeFormula,
	TweetTrendFormula,
	TweetVolumeFormula,
	UserTrendFormula,
	UserVolumeFormula,
)


class Listener():
	"""
	A listener combines a particular measurement index(Trend or TrendVolume)
	with a particular enzyme, so that you have, for example a listener for trending
	keywords and another for mentions volume
	"""

	def __init__(self, formula: Type[BaseFormula]) -> None:
		self._f = formula()
		self._base = None
	

	def __del__(self):
		self.stop_listen()


	def stop_listen(self):
		"""
		Stop all underlying tasks. This must be called so the event loop
		can exit normally
		"""
		if self._base:
			self._base.terminate()
			self._base = None


	async def listen(self):
		"""
		Start the listener to begin accepting Events
		"""
		self.stop_listen()
		self._base = await self._f.measure_class.make(
			self._f.enzyme_class,
			**self._f.get_kwargs()
		)
	

	async def notify(self, event: BaseEvent, pipe= None):
		"""
		Notify this listener of an event. If a pipe is passed, it must be
		manually executed after notify() returns or the changes will
		never be reflected
		"""
		if not self._base:
			raise RuntimeError("Listener is not listening. Call listen() first.")
		
		p = pipe or get_pipe()
		await self._base.notify(event, p)
		if not pipe:
			await p.execute()
	

	async def fetch(self, *args):
		"""
		args passed to fetch must match that expected by the underlying class
		"""
		if not self._base:
			raise RuntimeError("Listener is not listening. Call listen() first.")
		return await self._base.fetch(*args)


	def deconstruct(self):
		"""
		Collect underlying redis_object keys into a dict
		and save as json to redis
		"""
		return {self._f.deconstruct_key: self._base.deconstruct()}


keyword_trend_listener = Listener(KeywordTrendFormula)

tag_trend_listener = Listener(TagTrendFormula)

tweet_trend_listener = Listener(TweetTrendFormula)

user_trend_listener = Listener(UserTrendFormula)

keyword_volume_listener = Listener(KeywordVolumeFormula)

tag_volume_listener = Listener(TagVolumeFormula)

tweet_volume_listener = Listener(TweetVolumeFormula)

user_volume_listener = Listener(UserVolumeFormula)

all_listeners = [
	keyword_trend_listener,
	tag_trend_listener,
	tweet_trend_listener,
	user_trend_listener,
	keyword_volume_listener,
	tag_volume_listener,
	tweet_volume_listener,
	user_volume_listener,
]


async def start_all():
	"""
	Call listen on all listeners
	"""
	for listener in all_listeners:
		await listener.listen()


async def notify_all(event: BaseEvent):
	"""
	Notify all listeners of event
	"""
	pipe = get_pipe()
	for listener in all_listeners:
		await listener.notify(event, pipe)
	await pipe.execute()


def stop_all():
	"""
	Kill all listeners. May very well be restarted
	"""
	for listener in all_listeners:
		listener.stop_listen()


async def print_deconstruct():
	for l in all_listeners:
		print(l.deconstruct())