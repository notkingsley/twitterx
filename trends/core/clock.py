import asyncio


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
		"""
		Start the clock. 
		"""
		if self._running:
			return
		self._running = True
		self.make_task(self._run())


	def stop(self) -> None:
		"""
		Stop the clock from emitting more signals. 
		Clock may be restarted later with start()
		"""
		self._running = False