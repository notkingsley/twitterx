from django import template
from django.utils import timezone

register = template.Library()

@register.inclusion_tag("tweets/render_tweet.html")
def render_tweet_card(tweet, user):
	return {
		"tweet": tweet,
		"user": user,
	}


@register.inclusion_tag("tweets/render_multiple_tweets.html")
def render_multiple_tweets(tweets, user):
	return {
		"tweets": tweets,
		"user": user
	}


@register.filter("time_format")
def time_format(time: timezone.datetime):
	diff = timezone.now() - time
	if diff < timezone.timedelta(minutes= 1):
		return "Just now"
	elif diff < timezone.timedelta(hours= 1):
		return f"{diff.seconds // 60}m"
	elif diff < timezone.timedelta(days= 1):
		return f"{diff.seconds // 3600}h"
	elif diff < timezone.timedelta(days= 2):
		return "Yesterday"
	elif diff < timezone.timedelta(weeks= 1):
		return f"{diff.days // 7}d"
	elif time.year == timezone.now().year:
		return time.strftime("%b %-d")
	else:
		return time.strftime("%b %-d, %Y")