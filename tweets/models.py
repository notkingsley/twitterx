from django.db import models
from django.utils import timezone
from django.urls import reverse

class Tweet(models.Model):
	created = models.DateTimeField("Date created", auto_now_add= timezone.now)
	modified = models.DateTimeField("Last modified", )

	text = models.CharField(
		"Tweet",
		blank= False,
		max_length= 280,
	)

	author = models.ForeignKey(
		"users.User",
		models.CASCADE,
		"tweets",
		verbose_name= "Author",
	)

	in_reply_to = models.ForeignKey(
		"self",
		models.CASCADE,
		"replies",
		null= True,
		verbose_name= "Replies",
	)

	in_retweet_to = models.ForeignKey(
		"self",
		models.CASCADE,
		"retweets",
		null= True,
		verbose_name= "Retweets",
	)

	likes = models.ManyToManyField(
		"users.User",
		"all_likes",
		verbose_name= "Likes",
	)

	class Meta:
		ordering = ["-created"]
	

	def __str__(self) -> str:
		return self.text[:28] + "..."
	

	def get_absolute_url(self) -> str:
		return reverse("tweets:tweet", kwargs= {"pk": self.pk})
	

	def is_reply(self) -> bool:
		try:
			self.in_reply_to
			return True
		except:
			return False
	

	def is_retweet(self) -> bool:
		try:
			self.in_retweet_to
			return True
		except:
			return False