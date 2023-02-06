from django.views import generic

from . import models


class ProfileView(generic.DetailView):
	template_name: str = "users/profile.html"
	model = models.User
	slug_field: str = "username"
	slug_url_kwarg: str = "username"