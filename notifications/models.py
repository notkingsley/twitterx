from django.db import models
from django.utils import timezone


class NotificationBox(models.Model):
	user = models.OneToOneField(
		"users.User",
		models.CASCADE,
		related_name= "notification_box",
		editable= False,
	)


class Message(models.Model):
	body = models.CharField(
		"Notification message",
		max_length= 280,
	)

	link = models.URLField(
		"Redirect link",
	)

	created = models.DateTimeField(
		"Date created",
		auto_now_add= timezone.now
	)

	box = models.ForeignKey(
		NotificationBox,
		models.CASCADE,
		related_name= "messages",
		verbose_name= "Notification Box",
	)

	clicked = models.BooleanField(
		"Notification has been clicked",
	)

	class Meta:
		ordering = ["-created"]
	

	def __str__(self) -> str:
		return self.body