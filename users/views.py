from django.views import generic
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

from . import models

# TODO accept login by email

HOMEPAGE = reverse_lazy("twitterx:home")


class ProfileView(generic.DetailView):
	template_name: str = "users/profile.html"
	model = models.User
	slug_field: str = "username"
	slug_url_kwarg: str = "username"


class LoginView(auth_views.LoginView):
	template_name: str = "users/login.html"
	next_page = HOMEPAGE


class LogoutView(auth_views.LogoutView):
	next_page = HOMEPAGE