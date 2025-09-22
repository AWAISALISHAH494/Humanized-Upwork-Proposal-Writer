from __future__ import annotations

from dataclasses import dataclass
from typing import List, Set

import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


DEFAULT_SKILL_KEYWORDS: Set[str] = {
	"python", "javascript", "typescript", "react", "node", "django", "flask",
	"fastapi", "streamlit", "pandas", "numpy", "scikit", "ml", "nlp",
	"spacy", "nltk", "openai", "gpt", "gemini", "llm", "prompt",
	"api", "rest", "graphql", "aws", "gcp", "azure",
	"sql", "postgres", "mysql", "sqlite", "mongodb",
	"docker", "kubernetes", "ci", "cd", "git",
}


@dataclass
class SkillExtractor:
	custom_keywords: Set[str] | None = None

	def _normalize(self, text: str) -> List[str]:
		try:
			stop_words = set(stopwords.words("english"))
		except LookupError:
			stop_words = set()
		text = text.lower()
		text = re.sub(r"[^a-z0-9\s\-\+\.#]", " ", text)
		try:
			tokens = word_tokenize(text)
		except LookupError:
			tokens = text.split()
		return [t for t in tokens if t not in stop_words and len(t) > 1]

	def extract(self, text: str, top_k: int = 20) -> List[str]:
		tokens = self._normalize(text)
		keywords = set(t for t in tokens if t in (self.custom_keywords or DEFAULT_SKILL_KEYWORDS))
		# capture bigrams like "machine learning", "data science"
		joined = " ".join(tokens)
		for phrase in [
			"machine learning", "data science", "natural language", "deep learning",
			"large language", "generative ai", "computer vision",
		]:
			if phrase in joined:
				keywords.add(phrase)
		return sorted(list(keywords))[:top_k] 