import re

from django.db.models import signals
from django.contrib.auth import get_user_model


def register_all():
	signals.post_save.connect(_tweet_saved, "tweets.Tweet", dispatch_uid= "n:_tweet_saved")


def _tweet_saved(sender, **kwargs):
	if not kwargs["created"]:
		return
	
	instance = kwargs["instance"]
	notify_mentions(instance)
	notify_reply(instance)
	notify_retweet(instance)


def notify_like(tweet, user):
	"""
	Call when user likes tweet
	"""
	if tweet.author == user:
		return
	print(f"To {tweet.author}: {user} liked your tweet {tweet}. Link: {user.get_absolute_url()}")


def notify_follow(followed, user):
	"""
	Call when user follows followed
	"""
	if followed == user:
		raise RuntimeError("A user may not follow themself")
	print(f"To {followed}: {user} started following you. Link: {user.get_absolute_url()}")


def notify_mentions(tweet):
	"""
	Notify potential mentions in tweet
	"""
	for u in mentions_to_objects(extract_mentions(tweet.text)):
		notify_mention(tweet, u)


def notify_reply(tweet):
	"""
	Call when tweet is in reply to some user's tweet
	"""
	if not tweet.is_reply() or tweet.author == tweet.in_reply_to.author:
		return
	print(f"To {tweet.in_reply_to.author}: {tweet.author} replied to your tweet {tweet.in_reply_to}. Link: {tweet.get_absolute_url()}")


def notify_retweet(tweet):
	"""
	Call when tweet is in retweet to some user's tweet
	"""
	if not tweet.is_retweet() or tweet.author == tweet.in_retweet_to.author:
		return
	print(f"To {tweet.in_retweet_to.author}: {tweet.author} retweeted your tweet {tweet.in_retweet_to}. Link: {tweet.get_absolute_url()}")


def notify_mention(tweet, user):
	"""
	Call when user is mentioned in tweet
	"""
	if tweet.author == user:
		return
	print(f"To {user}: {tweet.author} mentioned you in a tweet. Link: {tweet.get_absolute_url()}")


def mentions_to_objects(mentions: list[str]):
	"""
	Tranform a list of potential usernames into user objects,
	filtering out invalids
	"""
	return get_user_model().objects.filter(username__in= mentions)


def extract_mentions(text: str) -> list[str]:
	"""
	Extract a list of potential mentions from text
	"""
	return [s[1:] for s in re.findall(r"@[\w]+", text)]