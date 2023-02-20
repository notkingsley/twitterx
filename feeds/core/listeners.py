import datetime
from typing import Type

from feeds.core.client import get_pipe
from feeds.core.enzymes import (
	BaseEnzyme,
	KeywordEnzyme,
	TagEnzyme, 
	TweetIdEnzyme,
	UserIdEnzyme,
)
from feeds.core.event import BaseEvent
from feeds.core.trend import Trend
from feeds.core.volume import TrendVolume


global_trend_intervals = [
	datetime.timedelta(seconds= 10),
	datetime.timedelta(minutes= 1),
	datetime.timedelta(minutes= 4),
	datetime.timedelta(minutes= 15),
	datetime.timedelta(hours= 1),
]

global_volume_interval = datetime.timedelta(hours= 60)


class Listener():
	"""
	A listener combines a particular measurement index(Trend or TrendVolume)
	with a particular enzyme, so that you have, for example a listener for trending
	keywords and another for mentions volume
	"""

	def __init__(self, measure_class, enzyme_class: Type[BaseEnzyme], **kwargs) -> None:
		self._base_class = measure_class
		self._enzyme_class = enzyme_class
		self._base = None
		self.kwargs = kwargs
	

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
		self._base = await self._base_class.make(self._enzyme_class, **self.kwargs)
	

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


trend_kwargs = {"intervals": global_trend_intervals}

volume_kwargs = {"interval": global_volume_interval}

keyword_trend_listener = Listener(Trend, KeywordEnzyme, **trend_kwargs)

tag_trend_listener = Listener(Trend, TagEnzyme, **trend_kwargs)

tweet_trend_listener = Listener(Trend, TweetIdEnzyme, **trend_kwargs)

user_trend_listener = Listener(Trend, UserIdEnzyme, **trend_kwargs)

keyword_volume_listener = Listener(TrendVolume, KeywordEnzyme, **volume_kwargs)

tag_volume_listener = Listener(TrendVolume, TagEnzyme, **volume_kwargs)

tweet_volume_listener = Listener(TrendVolume, TweetIdEnzyme, **volume_kwargs)

user_volume_listener = Listener(TrendVolume, UserIdEnzyme, **volume_kwargs)

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