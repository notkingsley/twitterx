from django.urls import path

from . import views

app_name = "users"
urlpatterns = [
	path("login/", views.LoginView.as_view(), name= "login"),
	path("logout/", views.LogoutView.as_view(), name= "logout"),
	path("signup/", views.SignupView.as_view(), name= "signup"),

	path("password/change/", views.PasswordChangeView.as_view(), name= "password_change"),
	path("password/change/done/", views.PasswordChangeDoneView.as_view(), name= "password_change_done"),
	path("password/reset/", views.PasswordResetView.as_view(), name= "password_reset"),
	path("password/reset/done/", views.PasswordResetDoneView.as_view(), name= "password_reset_done"),
	path("password/reset/confirm/<uidb64>/<token>/", views.PasswordResetConfirmView.as_view(), name= "password_reset_confirm"),
	path("password/reset/complete/", views.PasswordResetCompleteView.as_view(), name= "password_reset_complete"),
]