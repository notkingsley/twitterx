import asyncio
from collections import defaultdict
from typing import Type
import datetime

from .kstructures import KQueue
from .clock import Clock
from .enzymes import BaseEnzyme


class EventFrame():
	"""
	Manage a clock and a KQueue to represent concrete handle on
	the most frequent set of events that have happened in, say, 
	the last 4 hours

	This is a thin wrapper around KQueues, expects similar
	arguments and provides a similar interface
	"""

	def __init__(self, kqueue: KQueue, size, interval) -> None:
		"""
		Use make() to create EventFrames
		"""
		self._queue = kqueue
		self.interval = interval
		self._clock = Clock(self._queue.signal, self.interval / size)
		self.add = self._queue.add
		self.get = self._queue.get
		self.check = self._queue.check
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
		kq = await KQueue.make(maxlen=size, **kwargs)
		return EventFrame(kq, size, interval)


class Trend():
	"""
	Manage multiple eventframes with varying clock lengths
	Provide an interface to collect all top k trending
	elements on demand
	
	This class collects the results from the eventframes
	amd combines them in some time-weighted fashion to produce a list
	of the top k trending objects
	
	A trend object represents how frequent recent occurences of
	the most frequent objects has occured in recent streams.
	"""

	def __init__(self, enzyme_class: Type[BaseEnzyme]) -> None:
		"""
		Use make() to create Trend objects
		"""
		self._enzyme = enzyme_class()
		self._frames: list[EventFrame]
	

	def __del__(self):
		self.terminate()
	

	def terminate(self):
		for f in self._frames:
			f.stop()
	

	@classmethod
	async def make(
		cls,
		enzyme_class: Type[BaseEnzyme],
		intervals: list[datetime.timedelta],
		duplicity= 10,
		**kwargs
	):
		t = Trend(enzyme_class)
		t._frames = [
			await EventFrame.make(
				duplicity,
				i.seconds,
				**kwargs
			) for i in intervals
		]
		return t


	async def notify(self, event, pipe):
		"""
		Notify this trend of a new obj in the stream
		"""
		digest = self._enzyme.digest(event)
		for f in self._frames:
			for d in digest:
				await f.add(d, pipe)
	

	async def fetch(self, k= 20):
		"""
		Get the top k trending objects
		"""
		agg = await asyncio.gather(*[f.get() for f in self._frames])
		d = defaultdict(float)
		for interval, res in zip((f.interval for f in self._frames), agg):
			for key, val in res.items():
				d[key] += val / interval ** 2
		
		return [tp[0] for tp in sorted(
			d.items(),
			key= lambda item: item[1],
			reverse= True,
		)][:k]