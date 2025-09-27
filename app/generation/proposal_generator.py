from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from app.models.job_description import JobDescription
from app.models.user_profile import UserProfile
from app.nlp.skill_extractor import SkillExtractor
from app.data.experience_manager import ExperienceManager
from app.ai.provider_base import AIProvider
from app.generation.template_manager import TemplateManager


@dataclass
class ProposalGenerator:
	skill_extractor: SkillExtractor
	experience_manager: ExperienceManager
	ai_provider: AIProvider
	template_manager: TemplateManager

	def generate(
		self,
		job: JobDescription,
		style: str = "friendly",
		include_pricing: bool = True,
		temperature: float = 0.5,
		max_tokens: int = 1200,
		user: Optional[UserProfile] = None,
	) -> str:
		self.template_manager.style = style
		skills = self.skill_extractor.extract(job.cleaned_text(), top_k=20)
		relevant = self.experience_manager.relevant_projects(skills, top_k=3)
		prefix = f"{self.template_manager.greeting()}\n"
		body = self.ai_provider.generate_proposal(
			job_text=job.cleaned_text(),
			skills=skills,
			projects=relevant,
			style=style,
			include_pricing=include_pricing,
			temperature=temperature,
			max_tokens=max_tokens,
			user_profile=(user.summary() if user else None),
		)
		closing_name = f" {user.name}" if user and user.name else ""
		return prefix + body + f"\n{self.template_manager.closing()}{closing_name}\n" 