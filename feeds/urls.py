from django.urls import path

from . import views

app_name = "feeds"
urlpatterns = [
	path("feed/", views.Feed.as_view(), name= "feed"),
]