"""
Count-min sketch primitives
"""

import asyncio

from trends.core.client import get_global_client
from trends.core.redis_object import RedisObject, InvalidRedisObject
from trends.core.auto_queue import AutoQueue


class CMSketch(RedisObject):
	"""
	Handle low level redis connections and cms keys
	"""

	@classmethod
	async def make(cls, prefix= "cms", width= 100, depth= 10):
		cm = CMSketch(prefix)
		task = asyncio.create_task(
			get_global_client().cms().initbydim(
				cm._key,
				width,
				depth,
			)
		)
		task.add_done_callback(cm._validate)
		return cm
	

	async def add(self, obj, pipe=None):
		"""
		Increment count of obj in sketch by 1
		"""
		if not await self.ensure_valid():
			return
		client = pipe or get_global_client()
		await client.cms().incrby(self._key, [obj], [1])
	

	async def get(self, objs: list):
		"""
		Get count of each obj in objs in the order they were passed
		"""
		if not await self.ensure_valid():
			raise InvalidRedisObject
		if not objs:
			return []
		return await get_global_client().cms().query(self._key, *objs)


class CMQueue(AutoQueue):
	"""
	An AutoQueue with count-min sketches as underlying objects
	"""
	object_class = CMSketch

	async def get(self, objs: list) -> list[int]:
		async with self._lock:
			while True:
				try:
					return await self._deque[0].get(objs)
				except InvalidRedisObject:
					self._deque.popleft()