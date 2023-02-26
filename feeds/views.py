import json

from django.views import generic
from django.contrib.auth import mixins
from django.urls import reverse_lazy

from tweets.models import Tweet
from . import models


# TODO add reliable way to determine seen tweets and add
# times to user.feed.seen (front-end work, probably)
# TODO efficiently merge intervals in user.feed.seen
# when there isn't an obvious overlap, but no tweet
# created in-between

LOGIN_URL = reverse_lazy("users:login")

REDIRECT_FIELD_NAME = 'r'


def _ensure_feed(user):
	"""
	Create a Feed for this user if none exists.
	Consider listening to post-save signal on User instead
	"""
	try:
		user.feed
	except:
		models.Feed.objects.create(user= user)


class Feed(mixins.LoginRequiredMixin, generic.ListView):
	template_name: str = "feeds/feed.html"
	context_object_name = "tweets"
	login_url = LOGIN_URL
	redirect_field_name = REDIRECT_FIELD_NAME

	def get_queryset(self):
		_ensure_feed(self.request.user)
		q = Tweet.objects.filter(
			author__in= self.request.user.follows.all(),
			in_reply_to__isnull= True,
		)
		for pair in json.loads(self.request.user.feed.seen):
			q = q.exclude(created__range= pair)
		return q