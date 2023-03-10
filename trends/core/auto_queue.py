from abc import ABC
import asyncio
from collections import deque
from typing import Type

from trends.core.redis_object import RedisObject


class AutoQueue(ABC):
	"""
	Maintain a bounded deque of RedisObjects, constantly adding new ones 
	and deleting old ones. Expose the interface to the one on top of the
	deque (oldest one) and an interface to add elements to all simultaneously

	Objects nearer the top are older and will be removed sooner
	"""

	object_class: Type[RedisObject]

	def __init__(self, maxlen= 5, **kwargs) -> None:
		"""
		Initialize an AutoQueue with a maxsize of maxlen
		kwargs should be parameters for making RedisObjects
		The RedisObject is not guaranteed to be ready after this,
		use make() instead
		"""
		self._deque: deque[RedisObject] = deque(maxlen= maxlen)
		self._params = kwargs
		self._lock = asyncio.Lock()
	

	@classmethod
	async def make(cls, **kwargs):
		obj = cls(**kwargs)
		await obj.signal()
		return obj


	async def add(self, obj, pipe= None) -> None:
		"""
		Add obj to all elements in queue
		"""
		async with self._lock:
			for r in self._deque:
				await r.add(obj, pipe)
	

	async def get(self):
		"""
		Get from oldest RedisObject in queue
		"""
		async with self._lock:
			return await self._deque[0].get()
	

	async def signal(self) -> None:
		"""
		Create a new RedisObject, discarding any overflows
		"""
		if len(self._deque) == self._deque.maxlen:
			await self._deque[0].delete()
		async with self._lock:
			self._deque.append(await self.object_class.make(**self._params))
	

	@classmethod
	async def construct(cls, obj: dict):
		"""
		Construct an autoqueue from an old autoqueue state
		"""
		aq = cls(maxlen= obj["maxlen"], **obj["_params"])
		async with aq._lock:
			for r in obj["_deque"]:
				aq._deque.append(await cls.object_class.construct(r))
		return aq

	

	def deconstruct(self):
		"""
		Deconstruct each RedisObject in the deque to a dict
		"""
		return {
			"_deque": [r.deconstruct() for r in self._deque],
			"maxlen": self._deque.maxlen,
			"_params": self._params,
		}