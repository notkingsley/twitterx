from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth import mixins

from tweets.models import Tweet
from .core.fetch import get_trending_tweets

# TODO develop framework to produce volume of trends
# TODO write the tweet feeder

LOGIN_URL = reverse_lazy("users:login")

REDIRECT_FIELD_NAME = 'r'


class Feed(mixins.LoginRequiredMixin, generic.ListView):
	template_name: str = "feeds/feed.html"
	context_object_name = "tweets"
	login_url = LOGIN_URL
	redirect_field_name = REDIRECT_FIELD_NAME

	def get_queryset(self):
		t = get_trending_tweets()
		print(t)
		return Tweet.objects.filter(pk__in= t)