from django.urls import path

from . import views

app_name = "profiles"
urlpatterns = [
	path("edit/profile/", views.EditProfile.as_view(), name= "edit"),
	path("delete/profile/", views.DeleteProfile.as_view(), name= "delete"),
	path("edit/picture/", views.EditPicture.as_view(), name= "picture"),
	path("delete/picture/", views.DeletePicture.as_view(), name= "delete_picture"),

	path("u/<str:username>/", views.Profile.as_view(), name= "profile"),
	path("u/<str:username>/follow/", views.Follow.as_view(), name= "follow"),
]