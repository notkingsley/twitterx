"""
Functions to retreive trends from listeners
"""

import asyncio
import datetime

from feeds.core.listeners import (
	Listener,
	keyword_trend_listener,
	keyword_volume_listener,
	tag_trend_listener,
	tag_volume_listener,
	tweet_trend_listener,
	tweet_volume_listener,
	user_trend_listener,
	user_volume_listener,
)


_cache: dict[Listener: tuple[list, datetime.datetime]] = dict()

_CACHE_TIMEOUT = datetime.timedelta(seconds= 10)


def _get_from_listener(listener, *args):
	"""
	Schedule request in the event loop and wait for the result
	"""
	from feeds.core.loop import loop
	
	return asyncio.run_coroutine_threadsafe(
		listener.fetch(*args),
		loop,
	).result(), datetime.datetime.now()


def _expired(listener):
	"""
	Return True if cache entry for listener has expired
	"""
	return datetime.datetime.now() - _cache[listener][1] > _CACHE_TIMEOUT


def _resolve_with_cache(listener, *args, use_cache= True):
	"""
	Well, the name says it
	"""
	if not _cache.get(listener) or not use_cache or _expired(listener):
		_cache[listener] = _get_from_listener(listener, *args)
	return _cache[listener][0]


def get_trending_tweets(n= 20, use_cache= True) -> list[int]:
	return _resolve_with_cache(tweet_trend_listener, n, use_cache= use_cache)


def get_trending_tags(n= 20, use_cache= True) -> list[str]:
	return _resolve_with_cache(tag_trend_listener, n, use_cache= use_cache)


def get_trending_users(n= 20, use_cache= True) -> list[str]:
	return _resolve_with_cache(user_trend_listener, n, use_cache= use_cache)


def get_trending_keywords(n= 20, use_cache= True) -> list[str]:
	return _resolve_with_cache(keyword_trend_listener, n, use_cache= use_cache)


def get_tweets_volume(tweets: list[int], use_cache= True) -> list[int]:
	return _resolve_with_cache(tweet_volume_listener, tweets, use_cache= use_cache)


def get_tags_volume(tags: list[str], use_cache= True) -> list[int]:
	return _resolve_with_cache(tag_volume_listener, tags, use_cache= use_cache)


def get_users_volume(users: list[str], use_cache= True) -> list[int]:
	return _resolve_with_cache(user_volume_listener, users, use_cache= use_cache)


def get_keywords_volume(keywords: list[str], use_cache= True) -> list[int]:
	return _resolve_with_cache(keyword_volume_listener, keywords, use_cache= use_cache)