from django.urls import path

from . import views

app_name = "profiles"
urlpatterns = [
	path("edit/profile/", views.EditProfile.as_view(), name= "edit"),
	path("delete/profile/", views.DeleteProfile.as_view(), name= "delete"),
	path("edit/picture/", views.EditPictureView.as_view(), name= "picture"),

	path("u/<str:username>/", views.ProfileView.as_view(), name= "profile"),
	path("u/<str:username>/follow/", views.FollowView.as_view(), name= "follow"),
]