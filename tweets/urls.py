from django.urls import path

from . import views

app_name = "tweets"
urlpatterns = [
	path("t/<int:pk>/", views.Tweet.as_view(), name= "tweet"),
	path("t/<int:pk>/like/", views.Like.as_view(), name= "like"),
]