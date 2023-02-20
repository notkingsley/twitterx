from django.contrib.auth import get_user_model

from feeds.core.event import TweetEvent
from feeds.core.string import extract_keywords, extract_mentions, extract_tags


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
	from .core.loop import loop, queue
	
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
	d["keywords"] = extract_keywords(instance.text)
	
	loop.call_soon_threadsafe(queue.put_nowait, TweetEvent(**d))