from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth import mixins

from tweets.models import Tweet
from feeds.core import fetch


# TODO write the tweet feeder

LOGIN_URL = reverse_lazy("users:login")

REDIRECT_FIELD_NAME = 'r'


class Feed(mixins.LoginRequiredMixin, generic.ListView):
	template_name: str = "feeds/feed.html"
	context_object_name = "tweets"
	login_url = LOGIN_URL
	redirect_field_name = REDIRECT_FIELD_NAME

	def get_queryset(self):
		tweets = fetch.get_trending_tweets()
		users = fetch.get_trending_users()
		tags = fetch.get_trending_tags()
		print("tweets: ", tweets, fetch.get_tweets_volume(tweets))
		print("users: ", users, fetch.get_users_volume(users))
		print("tags: ", tags, fetch.get_tags_volume(tags))
		return Tweet.objects.filter(pk__in= tweets)