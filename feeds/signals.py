import asyncio
import threading

from django.contrib.auth import get_user_model

from .core.listener import listener
from .core.event import TweetEvent
from .core.string import extract_mentions, extract_tags

# TODO terminate created thread on server reload

loop: asyncio.AbstractEventLoop

queue: asyncio.Queue


def entry(ready: threading.Event):
	"""
	This runs in another thread, initializes an asyncio loop,
	the interface Queue and sets ready
	"""

	async def main():
		"""
		Entry point into async context
		Runs forever
		"""
		# start listening events here
		await listener.listen()

		ready.loop = asyncio.get_running_loop()
		ready.queue = event_queue = asyncio.Queue()
		ready.set()

		# run forever
		while True:
			event = await event_queue.get()

			# notify all listeners here
			asyncio.create_task(listener.notify(event))
		
		# stop listeners here. never runs as it is
		await listener.stop_listen()
	
	asyncio.run(main())


def start():
	"""
	Start the event loop in a separate thread
	"""
	loop_started = threading.Event()
	thread = threading.Thread(target= entry, args= [loop_started])
	thread.start()

	loop_started.wait()
	global loop, queue
	loop, queue = loop_started.loop, loop_started.queue


def mentions_to_id(mentions: list[str]):
	"""
	Tranform a list of potential usernames into user ids, 
	filtering out invalids
	"""
	return [pk for pk in get_user_model().objects.filter(
		username__in= mentions
	).values_list("pk", flat= True)]


def register_tweet_event(instance):
	"""
	Construct and register a TweetEvent
	"""
	
	d = dict()
	d["content"] = instance.text
	d["tweet_id"] = instance.pk
	d["user_id"] = str(instance.author.pk)

	if instance.is_reply():
		d["reply_id"] = instance.in_reply_to.pk
		d["reply_user_id"] = str(instance.in_reply_to.author.pk)
	if instance.is_retweet():
		d["retweet_id"] = instance.in_retweet_to.pk
		d["retweet_user_id"] = str(instance.in_retweet_to.author.pk)
	
	d["tags"] = extract_tags(instance.text)
	d["mentions_id"] = mentions_to_id(extract_mentions(instance.text))
	
	loop.call_soon_threadsafe(queue.put_nowait, TweetEvent(**d))