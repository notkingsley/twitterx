from django.urls import path

from . import views

app_name = "users"
urlpatterns = [
	path("login", views.LoginView.as_view(), name= "login"),
	path("logout", views.LogoutView.as_view(), name= "logout"),
	path("u/<str:username>/", views.ProfileView.as_view(), name= "profile"),
]