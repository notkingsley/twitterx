from django.views import generic

from . import models


class Tweet(generic.DetailView):
	template_name: str = "tweets/tweet.html"
	model = models.Tweet
	context_object_name = "tweet"