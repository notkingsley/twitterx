from django.views import generic
from django.contrib.auth import login, logout, mixins, views as auth_views
from django.urls import reverse_lazy

from . import models
from . import forms

# TODO accept login by email

HOMEPAGE = reverse_lazy("twitterx:home")

LOGIN_URL = reverse_lazy("users:login")

REDIRECT_FIELD_NAME = 'r'


class ProfileView(generic.DetailView):
	template_name: str = "users/profile.html"
	model = models.User
	slug_field: str = "username"
	slug_url_kwarg: str = "username"


class LoginView(auth_views.LoginView):
	template_name: str = "users/login.html"
	next_page = HOMEPAGE
	redirect_field_name = REDIRECT_FIELD_NAME


class LogoutView(auth_views.LogoutView):
	next_page = HOMEPAGE


class SignupView(generic.CreateView):
	template_name: str = "users/signup.html"
	form_class = forms.ProfileCreateForm

	def form_valid(self, form):
		ret = super().form_valid(form)
		login(self.request, form.instance)
		return ret


class EditProfile(mixins.LoginRequiredMixin, generic.UpdateView):
	template_name: str = "users/edit.html"
	fields = ["username", "email", "first_name", "last_name"]
	login_url = LOGIN_URL

	def get_object(self, queryset= None):
		return self.request.user


class DeleteProfile(mixins.LoginRequiredMixin, generic.DeleteView):
	template_name: str = "users/delete.html"
	model = models.User
	login_url = LOGIN_URL
	success_url = HOMEPAGE
	form_class = forms.ProfileDeleteForm

	def get_object(self, queryset= None):
		return self.request.user


	def get_form(self, form_class= None):
		form = super().get_form(form_class)
		form.expected = str(self.request.user)
		return form
	

	def form_valid(self, form):
		logout(self.request)
		return super().form_valid(form)