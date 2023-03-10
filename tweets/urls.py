from django.urls import path

from . import views

app_name = "tweets"
urlpatterns = [
	path("t/<int:pk>/", views.Tweet.as_view(), name= "tweet"),
	path("t/<int:pk>/like/", views.Like.as_view(), name= "like"),
	path("t/new/", views.NewTweet.as_view(), name= "new_tweet"),
	path("t/<int:pk>/delete/", views.DeleteTweet.as_view(), name= "delete"),
]