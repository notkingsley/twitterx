from django.contrib.auth.validators import UnicodeUsernameValidator, _

class UsernameValidator(UnicodeUsernameValidator):
	regex = r"^[^\W\d_][\w]{2,62}\Z"
	message = _(
		"The username must be between 3 and 63 character and may contain letters, "
		"numbers, and underscore and must start with a letter."
	)


class NameValidator(UnicodeUsernameValidator):
	regex = r"^[\w]{3,150}\Z"
	message = _(
		"The name must be between 3 and 150 character and may contain letters."
	)