from django.contrib.auth import forms as auth_forms

from . import models


class SignupForm(auth_forms.UserCreationForm):
	class Meta:
		model = models.User
		fields = (
			"username",
			"email",
			"first_name",
			"last_name",
		)