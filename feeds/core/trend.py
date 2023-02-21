import asyncio
from collections import defaultdict
from typing import Type
import datetime

# required so we can catch enzyme_class from globals()
from feeds.core.enzymes import *
from feeds.core.eventframe import EventFrame
from feeds.core.kstructures import KQueue


class TrendFrame(EventFrame):
	"""
	An EventFrame with KQueues as underlying queues
	Useful for determining trending items
	"""
	queue_class = KQueue


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
		self._frames: list[TrendFrame]
	

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
			await TrendFrame.make(
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
	

	@classmethod
	async def construct(self, obj: dict):
		"""
		An alternative to make() where an object returned by
		a previous deconstruct() is available
		"""
		t = Trend(globals()[obj["enzyme_class"]])
		t._frames = [await TrendFrame.construct(f) for f in obj["_frames"]]


	def deconstruct(self):
		"""
		Deconstruct each of the TrendFrames into a dict
		"""
		return {
			"_frames": [f.deconstruct() for f in self._frames],
			"enzyme_class": self._enzyme.__class__.__name__,
		}