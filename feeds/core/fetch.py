"""
Functions to retreive trends from listeners
"""

import asyncio
import datetime

from .listener import listener


_cache: dict[str: tuple[list, datetime.datetime]] = dict()

_CACHE_TIMEOUT = datetime.timedelta(seconds= 10)


def _get_from_listener(name, n):
	"""
	Schedule request in the event loop and wait for the result
	"""
	from .loop import loop
	
	return asyncio.run_coroutine_threadsafe(
		listener.get_trending(name, n),
		loop,
	).result(), datetime.datetime.now()


def _expired(name):
	"""
	Return True if cache entry with name has expired
	"""
	return datetime.datetime.now() - _cache[name][1] > _CACHE_TIMEOUT


def _resolve_with_cache(name, n, use_cache= True):
	"""
	Well, the name says it
	"""
	if not _cache.get(name) or not use_cache or _expired(name):
		_cache[name] = _get_from_listener(name, n)
	return _cache[name][0]


def get_trending_tweets(n= 20, use_cache= True) -> list[int]:
	return _resolve_with_cache("tweet_id", n, use_cache)


def get_trending_tags(n= 20, use_cache= True) -> list[str]:
	return _resolve_with_cache("tag", n, use_cache)


def get_trending_users(n= 20, use_cache= True) -> list[str]:
	return _resolve_with_cache("user_id", n, use_cache)


def get_trending_keywords(n= 20, use_cache= True):
	...