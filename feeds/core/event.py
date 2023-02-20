from abc import ABC

class BaseEvent(ABC):
	"""
	An event object containing information about
	some particular that has happened
	"""


class TweetEvent(BaseEvent):
	"""
	Someone has tweeted
	"""

	def __init__(
		self,
		content,
		tweet_id,
		user_id,
		*,
		reply_id= None,
		reply_user_id= None,
		retweet_id= None,
		retweet_user_id= None,
		tags= [],
		mentions_id= [],
		keywords= [],
	) -> None:
		self.text = content
		self.tweet_id = tweet_id
		self.user_id = user_id
		self.reply_id = reply_id
		self.reply_user_id = reply_user_id
		self.retweet_id = retweet_id
		self.retweet_user_id = retweet_user_id
		self.tags = tags
		self.mentions_id = mentions_id
		self.keywords = keywords
	

	def is_reply(self) -> bool:
		return self.reply_id and self.reply_user_id
	

	def is_reply(self) -> bool:
		return self.retweet_id and self.retweet_user_id