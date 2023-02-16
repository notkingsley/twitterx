from abc import ABC, abstractmethod
from collections import defaultdict, deque
import datetime

import asyncio
from typing import Type

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


class TaskManager():
	"""
	A convenient base class for classes that create and manage
	their own tasks
	"""

	_tasks: set[asyncio.Task] = set()

	@classmethod
	def make_task(cls, coro):
		"""
		Create and keep track of a task 
		"""
		task = asyncio.create_task(coro)
		cls._tasks.add(task)
		task.add_done_callback(cls._tasks.discard)
		return task
	

	@classmethod
	def kill_all(cls):
		for task in cls._tasks:
			task.cancel()
		cls._tasks.clear()


class Clock(TaskManager):
	"""
	Holds a reference to a callback signal it periodically
	"""

	def __init__(self, callback, interval: float, **kwargs) -> None:
		"""
		Initialize a clock with a callback that gets called
		every interval seconds with kwargs
		"""
		self._callback = callback
		self._interval = interval
		self._kwargs = kwargs
		self._running = False	
	

	async def _run(self) -> None:
		while self._running:
			await self._callback(**self._kwargs)
			await asyncio.sleep(self._interval)
	

	def start(self) -> None:
		if self._running:
			return
		self._running = True
		self.make_task(self._run())


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


class Enzyme(ABC):
	"""
	An enzyme is the signature behaviour of a trend object
	Only implementations of this class know the nature of the
	objects received from the stream and extract the required 
	parameter
	"""

	@abstractmethod
	def digest(self, obj):
		pass


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

	def __init__(self, enzyme_class: Type[Enzyme]) -> None:
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
		enzyme_class: Type[Enzyme],
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


	async def notify(self, obj, pipe):
		"""
		Notify this trend of a new obj in the stream
		"""
		digest = self._enzyme.digest(obj)
		for f in self._frames:
			await f.add(digest, pipe)
	

	async def fetch(self, k= 20):
		"""
		Get the top k trending objects
		"""
		agg = await asyncio.gather(*[f.get() for f in self._frames])
		d = defaultdict(float)
		for interval, res in zip((f.interval for f in self._frames), agg):
			for key, val in res.items():
				d[key] += val / interval ** 2
		
		return [tp for tp in sorted(
			d.items(),
			key= lambda item: item[1],
			reverse= True,
		)][:k]
	

class DummyEnzyme(Enzyme):
	def digest(self, obj):
		return obj


dummy_intervals = [
	datetime.timedelta(seconds= 3),
	datetime.timedelta(seconds= 5),
	datetime.timedelta(seconds= 10),
]


async def main():
	t = await Trend.make(DummyEnzyme, dummy_intervals)

	async def p(obj):
		print(obj)

	clocks: list[Clock] = list()
	for i in range(1, 10):
		clocks.append(Clock(t.notify, 10/i, obj= f"val{i}"))
		clocks[-1].start()
	print("all started")

	await asyncio.sleep(11)
	print("start fetching")
	for _ in range(10):
		print("fetched: ", await t.fetch())
		await asyncio.sleep(1)
	print("all fetched ")

	[clock.stop() for clock in clocks]
	t.terminate()
	await asyncio.gather(*Clock._tasks)
	await get_global_client().close()


async def main1():
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
	

if __name__ == "__main__":
	asyncio.run(main())


class Listener():
	"""
	Ideally, there will be a single listener object that maintains
	a set of all alive managers/topkqueues. Itself is signalled by
	the django signalling system for every new tweet, and passes the 
	tweet to the manager's enzyme to be digested
	"""