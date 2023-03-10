from django import forms


class ProfileDeleteForm(forms.Form):
	username = forms.CharField(
		label= "Username here",
		max_length= 150,
		empty_value= '@',
		required= True,
		error_messages= {"username": "Username does not match, please try again."},
	)

	expected: str = None

	def is_valid(self) -> bool:
		return self.expected == self.data['username'] and super().is_valid()