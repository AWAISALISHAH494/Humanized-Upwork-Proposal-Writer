from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class AIProvider(ABC):
	@abstractmethod
	def generate_proposal(
		self,
		job_text: str,
		skills: List[str],
		projects: List[Dict[str, str]],
		style: str = "friendly",
		include_pricing: bool = True,
		temperature: float = 0.7,
		max_tokens: int = 800,
		model: Optional[str] = None,
		user_profile: Optional[str] = None,
	) -> str:
		... 