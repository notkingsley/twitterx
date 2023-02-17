import asyncio

from django.contrib.auth import get_user_model

from .core.listener import listener
from .core.event import TweetEvent
from .core.string import extract_mentions, extract_tags

loop: asyncio.AbstractEventLoop


def start():
	"""
	Start all necessary tasks
	"""
	global loop
	loop = asyncio.get_running_loop()
	loop.create_task(listener.listen())


def mentions_to_id(mentions: list[str]):
	"""
	Tranform a list of potential usernames into user ids, 
	filtering out invalids
	"""
	return [pk for pk in get_user_model().objects.filter(
		username__in= mentions
	).values_list("pk", flat= True)]


def register_tweet_event(instance):
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
	
	print(f"Got {d}")

	def f():
		"""
		notify all listeners here
		passed arguments must be able to be evaluated in
		an asynchronous context
		"""
		asyncio.create_task(listener.notify(TweetEvent(**d)))

	loop.call_soon_threadsafe(f)