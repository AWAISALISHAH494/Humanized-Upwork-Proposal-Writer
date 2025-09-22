from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

import pandas as pd


@dataclass
class ExperienceManager:
	projects: List[Dict[str, str]] = field(default_factory=list)
	skills: List[str] = field(default_factory=list)

	def to_dataframe(self) -> pd.DataFrame:
		if not self.projects:
			return pd.DataFrame(columns=["title", "description", "tech", "impact"])
		return pd.DataFrame(self.projects)

	def add_project(self, title: str, description: str, tech: str, impact: str) -> None:
		self.projects.append({
			"title": title,
			"description": description,
			"tech": tech,
			"impact": impact,
		})

	def add_skills(self, skills: List[str]) -> None:
		for s in skills:
			if s not in self.skills:
				self.skills.append(s)

	def relevant_projects(self, keywords: List[str], top_k: int = 3) -> List[Dict[str, str]]:
		if not self.projects or not keywords:
			return self.projects[:top_k]
		kw = {k.lower() for k in keywords}
		def score(p: Dict[str, str]) -> int:
			text = f"{p.get('title','')} {p.get('description','')} {p.get('tech','')}".lower()
			return sum(1 for k in kw if k in text)
		return sorted(self.projects, key=score, reverse=True)[:top_k] 