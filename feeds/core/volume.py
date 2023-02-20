import asyncio
import datetime
from typing import Type

from feeds.core.cmsketch import CMQueue
from feeds.core.eventframe import EventFrame
from feeds.core.enzymes import BaseEnzyme


class BaseTrendVolume(EventFrame):
	"""
	EventFrame with a CMQueue as underlying queue class
	
	This allows retreival of how much of some certain object
	has occured in the specified interval, designed so trend
	volumes can be determined
	"""

	queue_class = CMQueue


class TrendVolume():
	"""
	This is a thin wrapper around BaseTrendVolume and handles
	enzymes and Events to provide a consistent interface
	"""

	def __init__(self, enzyme_class: Type[BaseEnzyme]) -> None:
		"""
		Use make() to instantiate TrendVolumes
		"""
		self._enzyme = enzyme_class()
		self._base: BaseTrendVolume
	

	def __del__(self):
		self.terminate()
	

	def terminate(self):
		self._base.stop()
	

	@classmethod
	async def make(
		cls,
		enzyme_class: Type[BaseEnzyme],
		interval: datetime.timedelta,
		duplicity= 200,
		**kwargs,
	):
		v = cls(enzyme_class)
		v._base = await BaseTrendVolume.make(
			duplicity,
			interval.seconds,
			**kwargs,
		)
		return v
	

	async def notify(self, event, pipe):
		"""
		Notify of a new event
		"""
		for digest in self._enzyme.digest(event):
			await self._base.add(digest, pipe)
	

	async def fetch(self, objs: list) -> list[int]:
		"""
		Get the count of elements of objs in that order
		"""
		return await self._base.get(objs)