from django.urls import path

from . import views


app_name = "notifications"
urlpatterns = [
	path("notifications/", views.Notifications.as_view(), name= "new"),
	path("notifications/all", views.AllNotifications.as_view(), name= "all"),
]