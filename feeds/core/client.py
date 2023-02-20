import asyncio
import atexit
from typing import Type
import redis.asyncio as redis


_client = redis.Redis(
	host= "localhost",
	port= 6379,
	decode_responses= True,
)


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
	
	coro = get_global_client().close()
	try:
		asyncio.create_task(coro)
	except RuntimeError:
		try:
			asyncio.run(coro)
		except RuntimeError:
			pass