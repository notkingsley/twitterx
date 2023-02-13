from django.views import generic
from django.contrib.auth import mixins
from django import http
from django.utils import timezone
from django.urls import reverse_lazy

from . import models


LOGIN_URL = reverse_lazy("users:login")

REDIRECT_FIELD_NAME = 'r'


class Tweet(generic.DetailView):
	template_name: str = "tweets/tweet.html"
	model = models.Tweet
	context_object_name = "tweet"


class Like(mixins.LoginRequiredMixin, generic.View):
	login_url = LOGIN_URL
	redirect_field_name = REDIRECT_FIELD_NAME

	def post(self, request, *args, **kwargs):
		try:
			tweet = models.Tweet.objects.get(pk= kwargs["pk"])
		except models.Tweet.DoesNotExist:
			return http.HttpResponseBadRequest()

		if request.user in tweet.likes.all():
			tweet.likes.remove(request.user)
		else:
			tweet.likes.add(request.user)

		tweet.save()
		return http.HttpResponse(status= 204)


class NewTweet(mixins.LoginRequiredMixin, generic.View):
	login_url = LOGIN_URL
	redirect_field_name = REDIRECT_FIELD_NAME
	
	def post(self, request, *args, **kwargs):
		reply_id = request.POST.get("reply_id")
		retweet_id = request.POST.get("retweet_id")
		text = request.POST.get("text")
		if not text or reply_id and retweet_id:
			return http.HttpResponseBadRequest()
		
		d = dict()
		if reply_id:
			try:
				d["in_reply_to"] = models.Tweet.objects.get(pk= reply_id)
			except models.Tweet.DoesNotExist:
				return http.HttpResponseBadRequest()
		if retweet_id:
			try:
				d["in_retweet_to"] = models.Tweet.objects.get(pk= retweet_id)
			except models.Tweet.DoesNotExist:
				return http.HttpResponseBadRequest()

		models.Tweet.objects.create(
			author= request.user,
			modified= timezone.now(),
			text= text,
			**d
		)
		return http.HttpResponse(status= 204)


class DeleteTweet(mixins.LoginRequiredMixin, generic.View):
	login_url = LOGIN_URL
	redirect_field_name = REDIRECT_FIELD_NAME

	def delete(self, request, *args, **kwargs):
		try:
			tweet = models.Tweet.objects.get(pk= kwargs["pk"])
		except models.Tweet.DoesNotExist:
			return http.HttpResponseBadRequest()

		if tweet.author != request.user:
			return http.HttpResponseForbidden()
		
		tweet.delete()
		return http.HttpResponseRedirect(
			request.POST.get(
				self.get_redirect_field_name(), 
				request.user.get_absolute_url()
			)
		)

	post = delete