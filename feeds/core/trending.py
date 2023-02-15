from collections import deque
import datetime

import asyncio

import redis.asyncio as redis


_client = redis.Redis(
	host= "localhost",
	port= 6379,
	decode_responses= True,
)


def get_global_client() -> redis.Redis:
	global _client
	return _client


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
		self.ensure_valid = self._valid.wait
	

	def __del__(self) -> None:
		"""
		Delete entry in redis
		"""
		self._valid.clear()
		print("deleting", self._key)
		asyncio.create_task(self._client.delete(self._key))
	

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
	

	async def add(self, obj, pipe= None) -> None:
		"""
		Add object to the topk
		"""
		await self.ensure_valid()
		client = pipe or self._client
		await client.topk().add(self._key, obj)
	

	async def get(self) -> dict:
		"""
		Return a dictionary of elements and their 
		respective counts
		"""
		await self.ensure_valid()
		ret = dict()
		l = await self._client.topk().list(self._key, True)
		for i in range(0, len(l), 2):
			ret[l[i]] = l[i + 1]
		return ret
	

	async def check(self, obj) -> bool:
		"""
		Check if obj is in top k elements
		"""
		await self.ensure_valid()
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


class Clock():
	"""
	Hold a reference to a KQueue and signal it periodically
	"""

	def __init__(self, queue: KQueue, interval: float) -> None:
		self._queue = queue
		self._interval = interval
		self._running = True
	

	async def run(self) -> None:
		while self._running:
			print("signalling")
			await self._queue.signal()
			await asyncio.sleep(self._interval)
	

	def start(self) -> None:
		self._running = True
		asyncio.create_task(self.run())


	def stop(self) -> None:
		self._running = False


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
		self._clock = Clock(self._queue, interval / size)
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


async def main():
	q = await EventFrame.make(8, 3)

	async def batch(q, num= 10, pipe= None):
		for j in range(num):
			for i in range(j):
				await q.add("val" + str(i), pipe)
		if pipe:
			await pipe.execute(False)
	
	for _ in range(10):
		now = datetime.datetime.now()
		await batch(q, 30, get_global_client().pipeline())
		print(datetime.datetime.now() - now)

		now = datetime.datetime.now()
		print(await q.get())
		print(datetime.datetime.now() - now)
	
	q.stop()
	print("sleeping to close")
	await asyncio.sleep(3)
	await get_global_client().close()
	

if __name__ == "__main__":
	asyncio.run(main())




class Manager():
	"""
	Manage multiple eventframes with varying clock lengths
	Provide an interface to collect all top k trending
	elements on demand
	
	This class collects the results from the eventframes
	amd combines them in some time-weighted fashion to produce a list
	of the top k trending objects
	
	Only one type of trending parameter should be used per object, for
	example, the tweet id
	"""


class Enzyme():
	"""
	An enzyme is the signature behaviour of a manager object
	It accepts tweet objects and the particular implementation
	decides which parameter to extract for the underlying topk filters,
	a tweet id for example
	"""


class Listener():
	"""
	Ideally, there will be a single listener object that maintains
	a set of all alive managers/topkqueues. Itself is signalled by
	the django signalling system for every new tweet, and passes the 
	tweet to the manager's enzyme to be digested
	"""