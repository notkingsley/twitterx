import asyncio
import atexit
import redis.asyncio as redis

from django.conf import settings


ACTIVE = False
_client = None

host = getattr(settings, "REDIS_HOST", None)
port = getattr(settings, "REDIS_PORT", None)

if host and port:
	_client = redis.Redis(
		host= host,
		port= port,
		decode_responses= True,
	)
	ACTIVE = True

# temporarily disable trends app
ACTIVE = False


def get_global_client() -> redis.Redis:
	global _client
	return _client


def get_pipe():
	return get_global_client().pipeline()


@atexit.register
def exit():
	"""
	Close connection
	May not be closed earlier because some kfilters still
	establish connections after the loop closes normally
	"""
	if not ACTIVE:
		return
		
	coro = get_global_client().close()
	try:
		asyncio.create_task(coro)
	except RuntimeError:
		try:
			asyncio.run(coro)
		except RuntimeError:
			pass