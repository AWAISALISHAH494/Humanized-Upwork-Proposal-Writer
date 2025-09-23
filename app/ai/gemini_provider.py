from __future__ import annotations

import os
from typing import Dict, List, Optional

try:
	import google.generativeai as genai
except Exception:
	genai = None  # type: ignore

from .provider_base import AIProvider


DEFAULT_SYSTEM = (
	"You are an expert Upwork proposal writer. Use a professional, confident tone. "
	"Write detailed, specific proposals that demonstrate understanding, outline a clear plan, and reduce client risk. "
	"Avoid generic fluff and buzzwords; be concise yet substantive, client-focused, and outcomes-driven. "
	"Do not include any greeting or sign-off; those are added separately."
)


class GeminiProvider(AIProvider):
	def __init__(self, api_key: Optional[str] = None, default_model: str = "gemini-1.5-flash") -> None:
		self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
		self.default_model = default_model
		self.available = bool(self.api_key and genai is not None)
		if self.available:
			genai.configure(api_key=self.api_key)

	def _fallback(self, job_text: str, skills: List[str], projects: List[Dict[str, str]], style: str, include_pricing: bool) -> str:
		lines = [
			f"Style: {style}",
			"Thank you for sharing your project. Here is how I would approach it professionally:",
			"\nUnderstanding & Goals:",
			"- I will review your current context, success criteria, and constraints to align scope.",
			"- I will confirm edge cases, must-haves, and nice-to-haves before implementation.",
			"\nRelevant Expertise:",
			f"- Skills: {', '.join(skills) if skills else 'Relevant domain and tooling expertise'}",
			"- Experience:",
		]
		for p in projects[:3]:
			lines.append(f"  • {p.get('title','Project')}: {p.get('impact','Delivered measurable impact')} ({p.get('tech','Tech')})")
		lines.extend([
			"\nProposed Approach:",
			"1) Discovery & validation — confirm requirements and success metrics.",
			"2) Implementation — develop features with iterative checkpoints.",
			"3) QA & refinement — resolve issues, polish UX, document usage.",
			"4) Handover — walkthrough, documentation, and support notes.",
			"\nDeliverables:",
			"- Functional implementation matching agreed scope",
			"- Documentation (setup, usage, and maintenance)",
			"- Optional Loom walkthrough if desired",
		])
		if include_pricing:
			lines.extend([
				"\nTimeline & Pricing (indicative):",
				"- Milestone 1: Discovery/Setup — 1–2 days",
				"- Milestone 2: Build — 2–4 days",
				"- Milestone 3: QA/Handover — 1–2 days",
				"Fixed or hourly available; happy to adjust to your preferences.",
			])
		lines.extend([
			"\nWhy Me:",
			"I deliver clear communication, reliable execution, and measurable outcomes aligned to your goals.",
			"I focus on pragmatic solutions and maintainability.",
			"\nNext Steps:",
			"If this aligns with your needs, I can start with a short kickoff to finalize scope.",
		])
		return "\n".join(lines)

	def generate_proposal(
		self,
		job_text: str,
		skills: List[str],
		projects: List[Dict[str, str]],
		style: str = "friendly",
		include_pricing: bool = True,
		temperature: float = 0.5,
		max_tokens: int = 1200,
		model: Optional[str] = None,
	) -> str:
		if not self.available:
			return self._fallback(job_text, skills, projects, style, include_pricing)

		project_list = "\n".join(
			f"- {p.get('title','Project')}: {p.get('description','')} (Tech: {p.get('tech','')}) — {p.get('impact','')}" for p in projects
		)
		prompt = (
			"Write a professional, detailed Upwork proposal body. Do NOT include any greeting or sign-off; those will be added outside.\n"
			"Use clear section headings and bullet points where helpful.\n"
			"Length: aim for 400–700 words if content warrants it.\n"
			f"Style: {style}. Maintain a confident, client-focused tone.\n\n"
			"Include these sections (adapt as needed):\n"
			"1) Understanding & goals (reflect the job description)\n"
			"2) Relevant expertise (skills + 2–3 concrete project highlights)\n"
			"3) Proposed approach (phases/steps)\n"
			"4) Deliverables and quality assurance\n"
			"5) Timeline (indicative)\n"
			"6) Pricing options or engagement model (optional)\n"
			"7) Why I’m a strong fit (tailored)\n"
			"8) Clear next step / CTA\n\n"
			f"Job Description:\n{job_text}\n\n"
			f"Skills to include: {', '.join(skills)}\n\n"
			f"Experience highlights:\n{project_list}\n"
		)

		model_name = model or self.default_model
		gem_model = genai.GenerativeModel(model_name)
		resp = gem_model.generate_content([
			{"role": "system", "parts": [DEFAULT_SYSTEM]},
			{"role": "user", "parts": [prompt]},
		], generation_config={
			"temperature": float(temperature),
			"max_output_tokens": int(max_tokens),
		})
		return (getattr(resp, "text", "") or "").strip() or self._fallback(job_text, skills, projects, style, include_pricing) 