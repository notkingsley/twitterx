import uuid

from django.views import generic
from django.contrib.auth import get_user_model

from tweets.models import Tweet
from trends.core import ACTIVE, fetch


class TrendingActive(generic.ListView):
	"""
	The Redis client is connected and this app is active
	"""
	template_name: str = "trends/trending.html"
	context_object_name = "tweets"

	def get_queryset(self):
		tweets = fetch.get_trending_tweets()
		return Tweet.objects.filter(pk__in= tweets)
	

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		tags = fetch.get_trending_tags()
		keywords = fetch.get_trending_keywords()
		users = fetch.get_trending_users()
		context["trending_tags"] = zip(
			tags,
			fetch.get_tags_volume(tags)
		)
		context["trending_keywords"] = zip(
			keywords,
			fetch.get_keywords_volume(keywords)
		)
		context["trending_users"] = zip(
			(get_user_model().objects.get(pk= uuid.UUID(user)) for user in users),
			fetch.get_users_volume(users)
		)
		return context


class TrendingInactive(generic.TemplateView):
	"""
	The Redis client is not connected and this app is inactive
	"""
	template_name: str = "trends/trending_inactive.html"


if ACTIVE:
	Trending = TrendingActive
else:
	Trending = TrendingInactive