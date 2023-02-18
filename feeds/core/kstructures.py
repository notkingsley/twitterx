"""
Low level data structures that interact with redis
top-k objects directly
"""

import asyncio

from .client import get_global_client
from .redis_object import RedisObject
from .auto_queue import AutoQueue

__all__ = ["KQueue"]


class KFilter(RedisObject):
	"""
	This class manages low-level redis keys and provides
	an interface for adding an element to it's underlying 
	redis data structure(top-k), and deleting that object when
	itself gets deleted
	
	KFilter objects are meant are meant to be dispensable
	"""

	@classmethod
	async def make(
		cls,
		prefix: str = "topk",
		k: int = 20,
		width= 8,
		depth= 7,
		decay= 0.9,
	):
		kf = KFilter(prefix)
		task = asyncio.create_task(
			get_global_client().topk().reserve(
				kf._key,
				k= k,
				width= width,
				depth= depth,
				decay= decay,
			)
		)
		task.add_done_callback(kf._validate)
		
		return kf
	

	async def add(self, obj, pipe= None) -> None:
		"""
		Add object to the topk
		"""
		if not await self.ensure_valid():
			return
		client = pipe or get_global_client()
		await client.topk().add(self._key, obj)
	

	async def get(self) -> dict:
		"""
		Return a dictionary of elements and their 
		respective counts
		"""
		if not await self.ensure_valid():
			return {}
		ret = dict()
		l = await get_global_client().topk().list(self._key, True)
		for i in range(0, len(l), 2):
			ret[l[i]] = l[i + 1]
		return ret


class KQueue(AutoQueue):
	"""
	An AutoQueue for handling KFilters
	"""
	object_class = KFilter