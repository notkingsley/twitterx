import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser, _
from django.urls import reverse_lazy

from . import validators


class User(AbstractUser):

	username_validator = validators.UsernameValidator()
	name_validator = validators.NameValidator()

	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	
	username = models.CharField(
		_("username"),
		max_length=150,
		unique=True,
		help_text=_(
			"Required. 3 to 63 characters. Letters, digits and underscore only."
		),
		validators= [username_validator],
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

	first_name = models.CharField(
		_("first name"), 
		max_length=150,
		validators= [name_validator],
	)

	last_name = models.CharField(
		_("last name"), 
		max_length=150,
		validators= [name_validator],
	)

	follows = models.ManyToManyField(
		"self",
		"followers",
		symmetrical= False,
	)

	profile_pic = models.ImageField(
		"Profile Picture",
		name= "profile_pic",
		upload_to= "profile_pics/%Y/%m/%d",
		default= "profile_pics/default.jpeg",
	)

	def __str__(self) -> str:
		return f"@{self.username}"

	
	def get_absolute_url(self) -> str:
		return reverse_lazy("profiles:profile", kwargs= {"username": self.username})
	

	def get_timeline_tweets(self):
		return self.tweets.filter(in_reply_to__isnull= True)