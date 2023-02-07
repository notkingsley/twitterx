from django.urls import path

from . import views

app_name = "users"
urlpatterns = [
	path("login/", views.LoginView.as_view(), name= "login"),
	path("logout/", views.LogoutView.as_view(), name= "logout"),
	path("signup/", views.SignupView.as_view(), name= "signup"),

	path("edit/profile/", views.EditProfile.as_view(), name= "edit"),
	path("delete/profile/", views.DeleteProfile.as_view(), name= "delete"),

	path("password/change/", views.PasswordChangeView.as_view(), name= "password_change"),
	path("password/change/done/", views.PasswordChangeDoneView.as_view(), name= "password_change_done"),
	
	path("u/<str:username>/", views.ProfileView.as_view(), name= "profile"),
]