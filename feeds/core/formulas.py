from abc import ABC, abstractmethod
import datetime
from typing import Type

from feeds.core.enzymes import (
	BaseEnzyme,
	KeywordEnzyme,
	TagEnzyme, 
	TweetIdEnzyme,
	UserIdEnzyme,
)
from feeds.core.trend import Trend
from feeds.core.volume import TrendVolume


__all__ = [
	"KeywordTrendFormula",
	"KeywordVolumeFormula",
	"TagTrendFormula",
	"TagVolumeFormula",
	"TweetTrendFormula",
	"TweetVolumeFormula",
	"UserTrendFormula",
	"UserVolumeFormula",
]


_global_trend_intervals = [
	datetime.timedelta(seconds= 10),
	datetime.timedelta(minutes= 1),
	datetime.timedelta(minutes= 4),
	datetime.timedelta(minutes= 15),
	datetime.timedelta(hours= 1),
]

_global_volume_interval = datetime.timedelta(hours= 60)


class BaseFormula(ABC):
	"""
	A Formula class contains the necessary parameters to
	easily instantiate a particular Listener
	"""
	measure_class: Type[Trend | TrendVolume]
	enzyme_class: BaseEnzyme
	deconstruct_key: str

	@abstractmethod
	def get_kwargs(self):
		return {}


class TrendFormulaMixin(BaseFormula):
	measure_class = Trend

	def get_kwargs(self):
		return {"intervals": _global_trend_intervals}


class TrendVolumeFormulaMixin(BaseFormula):
	measure_class = TrendVolume

	def get_kwargs(self):
		return {"interval": _global_volume_interval}


class KeywordEnzymeFormulaMixin(BaseFormula):
	enzyme_class = KeywordEnzyme


class TagEnzymeFormulaMixin(BaseFormula):
	enzyme_class = TagEnzyme


class TweetIdEnzymeFormulaMixin(BaseFormula):
	enzyme_class = TweetIdEnzyme


class UserIdEnzymeFormulaMixin(BaseFormula):
	enzyme_class = UserIdEnzyme


class KeywordTrendFormula(TrendFormulaMixin, KeywordEnzymeFormulaMixin):
	deconstruct_key = "keyword_trend"


class KeywordVolumeFormula(TrendVolumeFormulaMixin, KeywordEnzymeFormulaMixin):
	deconstruct_key = "keyword_volume"


class TagTrendFormula(TrendFormulaMixin, TagEnzymeFormulaMixin):
	deconstruct_key = "tag_trend"


class TagVolumeFormula(TrendVolumeFormulaMixin, TagEnzymeFormulaMixin):
	deconstruct_key = "tag_volume"


class TweetTrendFormula(TrendFormulaMixin, TweetIdEnzymeFormulaMixin):
	deconstruct_key = "tweet_trend"


class TweetVolumeFormula(TrendVolumeFormulaMixin, TweetIdEnzymeFormulaMixin):
	deconstruct_key = "tweet_volume"


class UserTrendFormula(TrendFormulaMixin, UserIdEnzymeFormulaMixin):
	deconstruct_key = "user_trend"


class UserVolumeFormula(TrendVolumeFormulaMixin, UserIdEnzymeFormulaMixin):
	deconstruct_key = "user_volume"