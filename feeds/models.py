from django.db import models


class Feed(models.Model):
	user = models.OneToOneField(
		"users.User",
		models.CASCADE,
		related_name= "feed",
		editable= False,
	)

	# seen is a json.dumps()ed list of 
	# datetime pairs in isoformat
	seen = models.TextField(
		"Time ranges of seen tweets",
		default= "[]",
	)