from django.views import generic
from django.contrib.auth import mixins
from django.urls import reverse_lazy

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
		return self.request.user.notification_box.messages.exclude(clicked= True)


class AllNotifications(Notifications):

	def get_queryset(self):
		_ensure_box(self.request.user)
		return self.request.user.notification_box.messages.all()