from django.urls import path

from . import views

app_name = "twitterx"
urlpatterns = [
	path("", views.HomeView.as_view(), name= "home"),
	path("about/", views.AboutView.as_view(), name= "about"),
	path("privacy/", views.PrivacyPolicyView.as_view(), name= "privacy"),
]