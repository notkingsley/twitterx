import re

from rake_nltk import Rake


def extract_tags(text: str) -> list[str]:
	return [s[1:] for s in re.findall(r"#[\w]+", text)]


def extract_mentions(text: str) -> list[str]:
	return [s[1:] for s in re.findall(r"@[\w]+", text)]


def extract_keywords(text: str) -> list[str]:
	"""
	This is not an adequate keyword exractor, but it 
	should serve as a good placeholder
	"""
	r = Rake()
	r.extract_keywords_from_text(text)
	return r.get_ranked_phrases()