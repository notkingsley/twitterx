"""
Low level data structures that interact with redis
top-k objects directly
"""

import asyncio
from collections import deque

from .client import redis, get_global_client

__all__ = ["KQueue"]


class KFilter():
	"""
	This class manages low-level redis keys and provides
	an interface for adding an element to it's underlying 
	redis data structure, and deleting that object when 
	itself gets deleted
	
	KFilter objects are meant are meant to be recyclable.
	"""

	def __init__(self, client: redis.Redis|None = None, prefix: str = "topk") -> None:
		"""
		Initialize internal variables. This does not create the top-k
		Use make() instead
		"""
		self._client = client or get_global_client()
		self._key = f"{prefix}:{id(self)}"
		self._valid = asyncio.Event()
		self._deleted = asyncio.Event()
	

	def __del__(self) -> None:
		"""
		Delete entry in redis
		"""
		self._deleted.set()
		self._valid.clear()
		coro = self._client.delete(self._key)
		try:
			asyncio.create_task(coro)
		except RuntimeError:
			try:
				asyncio.run(coro)
			except RuntimeError:
				pass
	

	def _validate(self, fut= None):
		"""
		Signal that the KFilter is stored in redis
		"""
		self._valid.set()
	

	@classmethod
	async def make(
		cls,
		client: redis.Redis|None = None,
		prefix: str = "topk",
		k: int = 20,
		width= 8,
		depth= 7,
		decay= 0.9,
	):
		kf = KFilter(client, prefix)
		task = asyncio.create_task(
			kf._client.topk().reserve(
				kf._key,
				k= k,
				width= width,
				depth= depth,
				decay= decay,
			)
		)
		task.add_done_callback(kf._validate)
		
		return kf
	

	async def ensure_valid(self):
		"""
		Verify that the filter is alive and valid
		Block until it is and return True, or return
		False if already deleted
		"""
		if self._deleted.is_set():
			return False
		return await self._valid.wait()
	

	async def add(self, obj, pipe= None) -> None:
		"""
		Add object to the topk
		"""
		if not await self.ensure_valid():
			return
		client = pipe or self._client
		await client.topk().add(self._key, obj)
	

	async def get(self) -> dict:
		"""
		Return a dictionary of elements and their 
		respective counts
		"""
		if not await self.ensure_valid():
			return {}
		ret = dict()
		l = await self._client.topk().list(self._key, True)
		for i in range(0, len(l), 2):
			ret[l[i]] = l[i + 1]
		return ret
	

	async def check(self, obj) -> bool:
		"""
		Check if obj is in top k elements
		"""
		if not await self.ensure_valid():
			return False
		return bool(await self._client.topk().query(self._key, obj)[0])


class KQueue():
	"""
	Maintain a limited deque of KFilters, constantly adding new ones 
	and deleting old ones. Expose the interface to the one on top of the
	deque (oldest one) and an interface to add elements to all simultaneously

	Filters near the top are older and will be removed sooner
	"""

	def __init__(self, maxlen= 5, **kwargs) -> None:
		"""
		Initialize a KQueue with a size of size
		kwargs should be a formula for making KFilters
		The KQueue is not guaranteed to be ready after this,
		use make() instead
		"""
		self._deque: deque[KFilter] = deque(maxlen= maxlen)
		self._params = kwargs
		self._lock = asyncio.Lock()
	

	@classmethod
	async def make(cls, **kwargs):
		kq = KQueue(**kwargs)
		await kq.signal()
		return kq


	async def signal(self) -> None:
		"""
		Create a new KFilter object, discarding any excesses
		"""
		async with self._lock:
			self._deque.append(await KFilter.make(**self._params))
	

	async def add(self, obj, pipe= None) -> None:
		"""
		Add obj to all elements in queue
		"""
		async with self._lock:
			for k in self._deque:
				await k.add(obj, pipe)
	

	async def get(self) -> dict:
		"""
		Get all k elements from oldest KFilter
		"""
		async with self._lock:
			return await self._deque[0].get()
	

	async def check(self, obj) -> bool:
		"""
		Check if obj is present in oldest KFilter
		"""
		async with self._lock:
			return await self._deque[0].check(obj)