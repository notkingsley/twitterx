from abc import ABC
from typing import Type

from feeds.core.clock import Clock
from feeds.core.auto_queue import AutoQueue


class EventFrame(ABC):
	"""
	Combine a clock and an AutoQueue to make the process of adding
	and removing RedisObjects automated. 
	This then represents a concrete handle on some set of events 
	that have happened in some defined interval, made consistent
	by the duplication in the underlying queue.

	Warning: instantiating an eventframe will leave tasks running
	in the event loop until the object dies or stop() is called
	This may lead to unexpected behaviour if you await asyncio.gather
	"""

	queue_class: Type[AutoQueue]

	def __init__(self, queue: AutoQueue, size, interval) -> None:
		"""
		Use make() to create EventFrames
		"""
		self._queue = queue
		self.interval = interval
		self._clock = Clock(self._queue.signal, self.interval / size)
		self.add = self._queue.add
		self.get = self._queue.get
		self.stop = self._clock.stop
		self._clock.start()
	

	def __del__(self) -> None:
		self._clock.stop()
	

	@classmethod
	async def make(cls, size, interval, **kwargs):
		"""
		Make a new EventFrame. kwargs are forwarded to the
		underlying kqueue
		size is the duplicity (more means less variance from 
		exact data interval seconds ago, but also means more memory)
		"""
		aq = await cls.queue_class.make(maxlen=size, **kwargs)
		return EventFrame(aq, size, interval)
	

	@classmethod
	async def construct(cls, obj: dict):
		"""
		Make an eventframe when the result of a previous deconstruct()
		is available. Resulting frame will try to refer to that old state's
		data, which may now be invalid
		"""
		aq = await cls.queue_class.construct(obj["_queue"])
		return EventFrame(aq, aq._deque.maxlen, obj["interval"])
	

	def deconstruct(self):
		"""
		Deconstruct or take a snapshot of the state
		of the underlying queue
		"""
		return {
			"_queue": self._queue.deconstruct(),
			"interval": self.interval,
		}