from django.views import generic
from django.contrib.auth import mixins
from django import http

from . import models


class Tweet(generic.DetailView):
	template_name: str = "tweets/tweet.html"
	model = models.Tweet
	context_object_name = "tweet"


class Like(mixins.LoginRequiredMixin, generic.View):

	def post(self, request, *args, **kwargs):
		tweet = models.Tweet.objects.get(pk= kwargs["pk"])
		if request.user in tweet.likes.all():
			tweet.likes.remove(request.user)
		else:
			tweet.likes.add(request.user)
		tweet.save()
		return http.HttpResponse(status= 204)
