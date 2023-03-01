from django.views import generic
from django.contrib.auth import mixins
from django.urls import reverse, reverse_lazy
from django import http

from . import models


LOGIN_URL = reverse_lazy("users:login")

REDIRECT_FIELD_NAME = 'r'


def _ensure_box(user):
	"""
	Ensure user has a notification box
	"""
	try:
		user.notification_box
	except:
		models.NotificationBox.objects.create(user= user)


class Notifications(mixins.LoginRequiredMixin, generic.ListView):
	login_url = LOGIN_URL
	redirect_field_name = REDIRECT_FIELD_NAME
	context_object_name = "messages"
	template_name = "notifications/notifications.html"

	def get_queryset(self):
		_ensure_box(self.request.user)
		return self.request.user.notification_box.get_new_messages()


class AllNotifications(Notifications):

	def get_queryset(self):
		_ensure_box(self.request.user)
		return self.request.user.notification_box.messages.all()


	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["all"] = True
		return context


class Click(mixins.LoginRequiredMixin, generic.View):
	login_url = LOGIN_URL
	redirect_field_name = REDIRECT_FIELD_NAME

	def post(self, request, *args, **kwargs):
		try:
			msg = models.Message.objects.get(pk= kwargs["pk"])
		except models.Message.DoesNotExist:
			return http.HttpResponseBadRequest()

		if msg.box.user != request.user:
			return http.HttpResponseForbidden()
		
		msg.clicked = True
		msg.save()
		return http.HttpResponseRedirect(msg.link)


class Clear(mixins.LoginRequiredMixin, generic.View):
	login_url = LOGIN_URL
	redirect_field_name = REDIRECT_FIELD_NAME

	def delete(self, request, *args, **kwargs):
		_ensure_box(request.user)
		request.user.notification_box.messages.all().delete()
		return http.HttpResponseRedirect(reverse("notifications:all"))

	post = delete