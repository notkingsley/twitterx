"""
This module handles starting and stopping of
the event loop
"""

import asyncio
import atexit
import os
import signal
import threading

from .client import get_global_client
from .clock import Clock
from .listener import listener


loop: asyncio.AbstractEventLoop = None

queue: asyncio.Queue = None


class Register():
	"""
	Register signals (os signals, not django) by 
	instantiating a menber of this class
	"""

	def __init__(self, signum, func) -> None:
		self.func = func
		self.old = signal.signal(signum, self)


	def __call__(self, signum, frame):
		self.func(signum, frame)

		if callable(self.old):
			self.old(signum, frame)
		elif self.old == signal.SIG_DFL:
			signal.signal(signum, signal.SIG_DFL)
			os.kill(os.getpid(), signal.SIG_DFL)
			self.old = signal.signal(signum, self)


def start():
	"""
	Start the event loop in a separate thread
	"""
	ready, quit = threading.Event(), threading.Event()

	def kill(*args):
		quit.set()
	
	Register(signal.SIGINT, kill)
	Register(signal.SIGTERM, kill)
	
	thread = threading.Thread(
		target= entry,
		args= [ready, quit],
		daemon= True
	)
	thread.start()
	ready.wait()


@atexit.register
def exit():
	"""
	Close connection
	May not be closed earlier because some kfilters still
	establish connections after the loop closes normally
	"""
	
	coro = get_global_client().close()
	try:
		asyncio.create_task(coro)
	except RuntimeError:
		try:
			asyncio.run(coro)
		except RuntimeError:
			pass


def entry(ready: threading.Event, quit: threading.Event):
	"""
	This runs in another thread, initializes an asyncio loop,
	the interface Queue and sets ready
	Exits when quit is set
	"""

	async def main():
		"""
		Entry point into async context
		"""

		try:
			await listener.listen()

			global loop, queue
			loop = asyncio.get_running_loop()
			queue = asyncio.Queue()
			ready.set()

			while True:
				try:
					event = await asyncio.wait_for(queue.get(), 1)
					asyncio.create_task(listener.notify(event))

				except asyncio.TimeoutError:
					if quit.is_set():
						break

		finally:
			listener.stop_listen()
			await asyncio.gather(*Clock._tasks)
	
	asyncio.run(main())