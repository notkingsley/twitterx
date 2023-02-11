from django.urls import path

from . import views

app_name = "tweets"
urlpatterns = [
	path("t/<int:pk>/", views.Tweet.as_view(), name= "tweet"),
]