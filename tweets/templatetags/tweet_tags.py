from django import template
from django.utils import timezone
from django.urls import reverse

register = template.Library()

@register.inclusion_tag("tweets/render_tweet.html")
def render_tweet(tweet, user):
	"""
	Render the tweet appropriately, including the retweet if any
	"""
	return {
		"tweet": tweet,
		"user": user,
	}


@register.inclusion_tag("tweets/render_multiple_tweets.html")
def render_multiple_tweets(tweets, user):
	"""
	Render an iterable of tweets, considering any possible retweets
	"""
	return {
		"tweets": tweets,
		"user": user,
	}


@register.inclusion_tag("tweets/render_retweet.html")
def render_retweet(tweet, user):
	"""
	Render a known retweet. Internal use only
	"""
	return {
		"tweet": tweet,
		"user": user,
	}


@register.inclusion_tag("tweets/render_single_tweet.html")
def render_single_tweet(tweet, user):
	"""
	Render a tweet, ignoring a possible retweet
	"""
	return {
		"tweet": tweet,
		"user": user,
	}


@register.inclusion_tag("tweets/render_tweet_head.html")
def render_tweet_head(tweet, user):
	"""
	Render a tweet's head and content. Internal use only
	"""
	return {
		"tweet": tweet,
		"user": user,
	}


@register.inclusion_tag("tweets/render_tweet_reactions.html")
def render_tweet_reactions(tweet, user):
	"""
	Render the bar containing like, comment and retweet buttons
	Internal use only
	"""
	return {
		"tweet": tweet,
		"user": user,
	}


@register.inclusion_tag("tweets/render_like_button.html")
def render_like_button(tweet, user):
	"""
	Render a like button to send a post request to tweet's like url
	"""
	return {
		"tweet": tweet,
		"user": user,
	}


@register.inclusion_tag("tweets/render_comment_button.html")
def render_comment_button(tweet, user):
	"""
	Render a comment button and the modal containing the form
	"""
	return {
		"tweet": tweet,
		"user": user,
	}


@register.inclusion_tag("tweets/render_tweet_button.html")
def render_tweet_button(user):
	"""
	Render a button to trigger a tweet modal
	"""
	return {"user": user}


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


@register.simple_tag(takes_context= True, name= "tracer")
def tracer(context):
	print(f"Tracer here. Context: {context}")