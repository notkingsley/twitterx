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
	

	@classmethod
	async def construct(cls, obj: str):
		"""
		Bind a RedisObject to an older key
		"""
		r = cls(obj)
		r._key = obj

		if await _check_exists(r._key):
			r._valid.set()
		else:
			r._deleted.set()
		return r
	

	def deconstruct(self):
		"""
		Return the key holding the redis object
		"""
		return self._key
	

	async def delete(self):
		"""
		Delete the entry in redis. This method must 
		called explicitly to free memory
		"""
		self._deleted.set()
		self._valid.clear()
		await get_global_client().delete(self._key)
	

async def _check_exists(key):
	"""
	Check that the an object exists at the given key
	"""
	return await get_global_client().exists(key)


class InvalidRedisObject(RuntimeError):
	pass