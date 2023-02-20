from abc import ABC, abstractmethod
import asyncio

import ulid

from feeds.core.client import get_global_client


class RedisObject(ABC):
	"""
	Base class defining methods common to classes
	interfacing with redis
	"""
	
	def __init__(self, prefix) -> None:
		"""
		Initialize internal variables. This does not create redis object
		Use make() instead
		"""
		self._key = f"{prefix}:{ulid.new().str}"
		self._valid = asyncio.Event()
		self._deleted = asyncio.Event()


	def __del__(self) -> None:
		"""
		Delete entry in redis
		"""
		self._deleted.set()
		self._valid.clear()
		coro = get_global_client().delete(self._key)
		try:
			asyncio.create_task(coro)
		except RuntimeError:
			try:
				asyncio.run(coro)
			except RuntimeError:
				pass


	def _validate(self, fut= None):
		"""
		Signal that the object is stored in redis
		"""
		self._valid.set()
	

	@classmethod
	@abstractmethod
	async def make(cls, **kwargs):
		...
	

	async def ensure_valid(self):
		"""
		Verify that the object is alive and valid
		Block until it is and return True, or return
		False if already deleted
		"""
		if self._deleted.is_set():
			return False
		return await self._valid.wait()
	

	@abstractmethod
	async def add(self, obj, pipe= None):
		...
	

	@abstractmethod
	async def get(self):
		...
	

	def deconstruct(self):
		"""
		Return the key holding the redis object
		"""
		return self._key


class InvalidRedisObject(RuntimeError):
	pass