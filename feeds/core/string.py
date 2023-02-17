import re


def extract_tags(text: str) -> list[str]:
	return [s[1:] for s in re.findall(r"#[\w]+", text)]


def extract_mentions(text: str) -> list[str]:
	return [s[1:] for s in re.findall(r"@[\w]+", text)]