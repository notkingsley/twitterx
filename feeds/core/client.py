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


def get_pipe() -> Type[redis.Redis.pipeline]:
	return get_global_client().pipeline()