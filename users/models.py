import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser, _
from django.urls import reverse

# TODO disallow @ . and + in usernames 
# TODO disallow usernames less than 3 letter
# TODO add a profile picture

class User(AbstractUser):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	
	username = models.CharField(
		_("username"),
		max_length=150,
		unique=True,
		help_text=_(
			"Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
		),
		validators=[AbstractUser.username_validator],
		error_messages={
			"unique": _("That username is already in use"),
		},
	)

	email = models.EmailField(
		_("email address"),
		unique= True,
		error_messages={
			"unique": _("That email address is already in use"),
		},
	)

	first_name = models.CharField(_("first name"), max_length=150)
	last_name = models.CharField(_("last name"), max_length=150)

	follows = models.ManyToManyField(
		"self",
		"followers",
		symmetrical= False,
	)

	def __str__(self) -> str:
		return f"@{self.username}"

	
	def get_absolute_url(self) -> str:
		return reverse("users:profile", kwargs= {"username": self.username})