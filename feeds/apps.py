from django.apps import AppConfig
from django.db.models.signals import post_save
from django.dispatch import receiver


class FeedsConfig(AppConfig):
	default_auto_field = 'django.db.models.BigAutoField'
	name = 'feeds'

	def ready(self) -> None:
		from . import signals

		# signals.start()

		@receiver(post_save, sender= "tweets.Tweet", dispatch_uid= "new_tweet", weak= False)
		def new_tweet(sender, **kwargs):
			return
			if not kwargs["created"]:
				print("tweet event denied")
				return
			signals.register_tweet_event(kwargs["instance"])