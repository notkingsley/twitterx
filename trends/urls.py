from django.urls import path

from . import views

app_name = "trends"
urlpatterns = [
	path("trending/", views.Trending.as_view(), name= "trending"),
]