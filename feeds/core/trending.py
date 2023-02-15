from collections import deque
import datetime
from threading import Thread, Lock
from time import sleep

import redis


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

	def __init__(
		self, 
		client: redis.Redis|None = None,
		k: int = 20,
		prefix: str = "topk",
		width= 8,
		depth= 7,
		decay= 0.9
	) -> None:
		self._client = client or get_global_client()
		self._key = f"{prefix}:{id(self)}"
		self._client.topk().reserve(
			self._key,
			k= k,
			width= width,
			depth= depth,
			decay= decay,
		)
	

	def __del__(self) -> None:
		"""
		Delete entry in redis
		"""
		self._client.delete(self._key)
	

	def add(self, obj, pipe= None) -> None:
		"""
		Add object to the topk
		"""
		client = pipe or self._client
		client.topk().add(self._key, obj)
	

	def get(self) -> dict:
		"""
		Return a dictionary of elements and their 
		respective counts
		"""
		ret = dict()
		l = self._client.topk().list(self._key, True)
		for i in range(0, len(l), 2):
			ret[l[i]] = l[i + 1]
		return ret
	

	def check(self, obj) -> bool:
		"""
		Check if obj is in top k elements
		"""
		return bool(self._client.topk().query(self._key, obj)[0])


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
		"""
		self._deque: deque[KFilter] = deque(maxlen= maxlen)
		self._params = kwargs
		self._lock = Lock() # lock so signal() doesn't change deque while reading
		self.signal()


	def signal(self) -> None:
		"""
		Create a new KFilter object, discarding any excesses
		"""
		with self._lock:
			self._deque.append(KFilter(**self._params))
	

	def add(self, obj, pipe= None) -> None:
		"""
		Add obj to all elements in queue
		"""
		with self._lock:
			for k in self._deque:
				k.add(obj, pipe)
	

	def get(self) -> dict:
		"""
		Get all k elements from oldest KFilter
		"""
		with self._lock:
			return self._deque[0].get()
	

	def check(self, obj) -> bool:
		"""
		Check if obj is present in oldest KFilter
		"""
		with self._lock:
			return self._deque[0].check(obj)


class Clock(Thread):
	"""
	Hold a reference to a KQueue and signal it periodically
	"""

	def __init__(self, queue: KQueue, interval: float) -> None:
		super().__init__()
		self._queue = queue
		self._interval = interval
		self._running = True
	

	def run(self) -> None:
		while self._running:
			print("signalling")
			self._queue.signal()
			sleep(self._interval)
	

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

	def __init__(self, size, interval, **kwargs) -> None:
		"""
		Make a new EventFrame. kwargs are forwarded to the
		underlying kqueue
		size is the duplicity (more means less variance from 
		exact data interval seconds ago, but also means more memory)
		"""
		self._queue = KQueue(maxlen=size, **kwargs)
		self._clock = Clock(self._queue, interval / size)
		self.add = self._queue.add
		self.get = self._queue.get
		self.check = self._queue.check
		self._clock.start()
	

	def __del__(self) -> None:
		self._clock.stop()


def main():
	q = EventFrame(8, 1)

	def batch(q, num= 10, pipe= None):
		for j in range(num):
			for i in range(j):
				q.add("val" + str(i), pipe)
		if pipe:
			pipe.execute(False)
	
	for _ in range(10):
		now = datetime.datetime.now()
		batch(q, 30, get_global_client().pipeline())
		print(datetime.datetime.now() - now)

		now = datetime.datetime.now()
		print(q.get())
		print(datetime.datetime.now() - now)
	

if __name__ == "__main__":
	main()


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