from django.apps import AppConfig
from django.db.models.signals import post_save
from django.dispatch import receiver


class FeedsConfig(AppConfig):
	default_auto_field = 'django.db.models.BigAutoField'
	name = 'feeds'

	def ready(self) -> None:
		from . import signals
		from .core import loop

		loop.start()

		@receiver(post_save, sender= "tweets.Tweet", dispatch_uid= "new_tweet", weak= False)
		def new_tweet(sender, **kwargs):
			# if not kwargs["created"]:
				# return
			signals.register_tweet_event(kwargs["instance"])