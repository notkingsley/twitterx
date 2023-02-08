from django.views import generic
from django.contrib.auth import login, logout, mixins, views as auth_views
from django.urls import reverse_lazy
from django import http

from . import forms, models

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

	def post(self, request, *args, **kwargs):
		try:
			user = models.User.objects.get(email= request.POST.get("username", ""))
			post = request.POST.copy()
			post["username"] = user.username
			request.POST = post
		except models.User.DoesNotExist:
			pass
		return super().post(request, *args, **kwargs)


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


class PasswordChangeView(auth_views.PasswordChangeView):
	template_name: str = "users/password_change.html"
	success_url = reverse_lazy("users:password_change_done")


class PasswordChangeDoneView(auth_views.PasswordChangeDoneView):
	template_name: str = "users/password_change_done.html"


class PasswordResetView(auth_views.PasswordResetView):
	template_name: str = "users/password_reset.html"
	email_template_name: str = "users/password_reset_email.html"
	subject_template_name: str = "users/password_reset_subject.txt"
	success_url = reverse_lazy("users:password_reset_done")


class PasswordResetDoneView(auth_views.PasswordResetDoneView):
	template_name: str = "users/password_reset_done.html"


class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
	template_name: str = "users/password_reset_confirm.html"
	success_url = reverse_lazy("users:password_reset_complete")


class PasswordResetCompleteView(auth_views.PasswordResetCompleteView):
	template_name: str = "users/password_reset_complete.html"


class FollowView(mixins.LoginRequiredMixin, generic.View):

	def post(self, request, *args, **kwargs):
		try:
			user = models.User.objects.get(username= kwargs["username"])
			if user == request.user:
				return http.HttpResponseBadRequest()

			if user in request.user.follows.all():
				request.user.follows.remove(user)
			else:
				request.user.follows.add(user)
			return http.HttpResponse(status= 204)
			
		except models.User.DoesNotExist:
			return http.HttpResponseBadRequest()