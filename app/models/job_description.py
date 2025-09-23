from __future__ import annotations

from dataclasses import dataclass
from typing import List

from pydantic import BaseModel, Field


class JobDescription(BaseModel):
	raw_text: str = Field(min_length=1, description="Original job description text")
	title: str | None = Field(default=None, description="Optional parsed job title")
	platform: str | None = Field(default="Upwork", description="Source platform")

	def cleaned_text(self) -> str:
		text = self.raw_text.strip()
		return " ".join(text.split())

	def to_bullets(self, max_items: int = 12) -> List[str]:
		text = self.cleaned_text()
		separators = ["- ", "• ", "\n", "; "]
		bullets: List[str] = []
		for sep in separators:
			if sep.strip() in text:
				parts = [p.strip("-• \t\r\n") for p in text.split(sep) if p.strip()]
				bullets.extend(parts)
				break
		if not bullets:
			bullets = [text]
		return bullets[:max_items] 