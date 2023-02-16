import datetime

from .client import get_pipe
from .enzymes import all_enzymes
from .event import BaseEvent
from .trend import Trend


global_intervals = [
	datetime.timedelta(seconds= 3),
	datetime.timedelta(seconds= 5),
	datetime.timedelta(seconds= 10),
]

class Listener():
	"""
	Listeners connct to a signalling system producing
	a stream of Events and pass them to their underlying
	trends to be digested.

	An useful extension would include a pluggable Filter class whose
	implementations define which events are actually processed, say,
	by geographical data.
	"""

	def __init__(self) -> None:
		self.trends: dict[str, Trend] = dict()
	

	def __del__(self):
		self.stop_listen()
	

	def stop_listen(self):
		for trend in self.trends.values():
			trend.terminate()
		self.trends.clear()

	async def listen(self, enzyme_classes= all_enzymes, intervals= global_intervals):
		"""
		Start up the trends so the listener can start accepting
		events
		"""
		for enzyme_class in enzyme_classes:
			self.trends[enzyme_class.name] = await Trend.make(enzyme_class, intervals)
	

	async def notify(self, event: BaseEvent, pipe= None):
		"""
		Notify this listener of an event. A filter would sit here
		If a pipe is passed, it should be executed after notify()
		returns or the changes will never be reflected
		"""
		if not self.trends:
			raise RuntimeError("Listener is not listening. Call listen() first.")

		p = pipe or get_pipe()
		for trend in self.trends.values():
			await trend.notify(event, p)
			
		if not pipe:
			await p.execute()
	

	async def get_trending(self, name: str, n= 20):
		"""
		Get top n trending objects by name
		"""
		if not self.trends:
			raise RuntimeError("Listener is not listening. Call listen() first.")
		return await self.trends[name].fetch(n)


listener = Listener()