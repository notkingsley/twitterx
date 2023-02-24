from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth import mixins

from tweets.models import Tweet
from trends.core import fetch


LOGIN_URL = reverse_lazy("users:login")

REDIRECT_FIELD_NAME = 'r'


class Feed(mixins.LoginRequiredMixin, generic.ListView):
	template_name: str = "trends/trending.html"
	context_object_name = "tweets"
	login_url = LOGIN_URL
	redirect_field_name = REDIRECT_FIELD_NAME

	def get_queryset(self):
		tweets = fetch.get_trending_tweets()
		return Tweet.objects.filter(pk__in= tweets)
	

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		tags = fetch.get_trending_tags()
		keywords = fetch.get_trending_keywords()
		context["trending_tags"] = dict(zip(
			tags,
			fetch.get_tags_volume(tags)
		))
		context["trending_keywords"] = dict(zip(
			keywords,
			fetch.get_keywords_volume(keywords)
		))
		return context