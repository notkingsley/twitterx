from django.views import generic
from django.contrib.auth import login, views as auth_views
from django.urls import reverse_lazy

from . import forms, models


HOMEPAGE = reverse_lazy("twitterx:home")

REDIRECT_FIELD_NAME = 'r'


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
	form_class = forms.SignupForm

	def form_valid(self, form):
		ret = super().form_valid(form)
		login(self.request, form.instance)
		return ret


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