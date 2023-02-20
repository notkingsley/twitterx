from abc import ABC, abstractmethod

from .event import BaseEvent, TweetEvent


class BaseEnzyme(ABC):
	"""
	An enzyme is the signature behaviour of a trend object
	Only implementations of this class know the nature of the
	objects received from the stream and extract the required 
	parameter
	"""

	name = "base_enzyme"

	@abstractmethod
	def digest(self, event: BaseEvent) -> list:
		...


class DummyEnzyme(BaseEnzyme):
	"""
	Return the event that was passed in
	"""
	
	def digest(self, event):
		return event


class TweetIdEnzyme(BaseEnzyme):
	"""
	Return all tweets involved with this particular tweet
	"""

	name = "tweet_id"

	def digest(self, event: BaseEvent) -> list:
		if not isinstance(event, TweetEvent):
			return []
		return[
			id for id in [
				event.tweet_id,
				event.reply_id,
				event.retweet_id,
			] if id
		]


class UserIdEnzyme(BaseEnzyme):
	"""
	Generate all user id's involved in a tweet event
	"""

	name = "user_id"

	def digest(self, event: BaseEvent) -> list:
		if not isinstance(event, TweetEvent):
			return []
		return [
			id for id in [
				event.user_id,
				event.reply_user_id,
				event.retweet_user_id,
			] if id
		] + event.mentions_id


class TagEnzyme(BaseEnzyme):
	"""
	Return all tags that this tweet made
	"""

	name = "tag"

	def digest(self, event: BaseEvent) -> list:
		if not isinstance(event, TweetEvent):
			return []
		return event.tags


class KeywordEnzyme(BaseEnzyme):
	"""
	Extract relevant keywords from text
	"""

	name = "keyword"

	def digest(self, event: BaseEvent) -> list:
		if not isinstance(event, TweetEvent):
			return []
		return event.keywords