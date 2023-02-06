from django.urls import path

from . import views

app_name = "users"
urlpatterns = [
	path("u/<str:username>/", views.ProfileView.as_view(), name= "profile"),
]