from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import streamlit as st
from rich.console import Console

from app.models.job_description import JobDescription
from app.nlp.skill_extractor import SkillExtractor
from app.data.experience_manager import ExperienceManager
from app.ai.openai_provider import OpenAIProvider
from app.generation.template_manager import TemplateManager
from app.generation.proposal_generator import ProposalGenerator


console = Console()


@dataclass
class Dashboard:
	generator: ProposalGenerator

	@staticmethod
	def default() -> "Dashboard":
		skill_extractor = SkillExtractor()
		experience_manager = ExperienceManager(
			projects=[
				{"title": "AI Proposal Writer", "description": "Built LLM-powered proposal generator", "tech": "Python, Streamlit, OpenAI", "impact": "Increased reply rate by 35%"},
				{"title": "NLP Skill Extractor", "description": "Extracted tech skills from text", "tech": "spaCy, NLTK", "impact": "Improved matching by 22%"},
			],
			skills=["python", "streamlit", "openai", "nlp"],
		)
		provider = OpenAIProvider()
		templates = TemplateManager(style="friendly")
		generator = ProposalGenerator(skill_extractor, experience_manager, provider, templates)
		return Dashboard(generator)

	def render(self) -> None:
		st.set_page_config(page_title="Humanized Upwork Proposal Writer", page_icon="📝", layout="wide")
		st.title("Humanized Upwork Proposal Writer")
		st.caption("Paste a job description and generate a tailored, human-like proposal.")

		with st.sidebar:
			st.header("Options")
			style = st.selectbox("Proposal style", ["friendly", "formal", "concise"], index=1)
			include_pricing = st.checkbox("Suggest pricing/delivery", value=True)
			temperature = st.slider("Creativity (lower is more professional)", 0.0, 1.2, 0.5, 0.05)
			max_tokens = st.slider("Max tokens (length)", 400, 1600, 1200, 50)

		col1, col2, col3 = st.columns([1, 1, 1])
		with col1:
			generate_clicked = st.button("Generate Proposal", type="primary")
		with col2:
			clear_clicked = st.button("Clear")
		with col3:
			load_sample = st.button("Load sample")

		# Handle state changes BEFORE creating text widgets
		if load_sample:
			st.session_state["job_text"] = "We need a Streamlit developer to build an AI-powered text tool..."
			st.rerun()

		if clear_clicked:
			st.session_state["job_text"] = ""
			st.session_state.pop("proposal_text", None)
			st.rerun()

		# Bind text area to session state for sample/clear actions
		st.text_area("Job description", height=260, placeholder="Paste the Upwork job description here...", key="job_text")
		job_text = st.session_state.get("job_text", "")

		proposal_text: Optional[str] = st.session_state.get("proposal_text")

		if generate_clicked and job_text.strip():
			job = JobDescription(raw_text=job_text)
			with st.spinner("Generating proposal..."):
				try:
					proposal_text = self.generator.generate(job, style=style, include_pricing=include_pricing, temperature=temperature, max_tokens=max_tokens)
					st.session_state["proposal_text"] = proposal_text
				except Exception as e:
					console.print(f"[red]Generation error:[/red] {e}")
					st.error("Failed to generate proposal. Using fallback.")
					proposal_text = None

		if proposal_text:
			st.subheader("Generated Proposal")
			edited = st.text_area("Edit before sending", value=proposal_text, height=420)
			st.session_state["proposal_text"] = edited

			colA, colB, colC = st.columns([1, 1, 1])
			with colA:
				st.download_button("Download .txt", data=edited, file_name="proposal.txt", mime="text/plain")
			with colB:
				try:
					from docx import Document
					doc = Document()
					doc.add_paragraph(edited)
					from io import BytesIO
					bio = BytesIO()
					doc.save(bio)
					st.download_button("Download .docx", data=bio.getvalue(), file_name="proposal.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
				except Exception:
					st.caption("DOCX export unavailable.")
			with colC:
				st.caption("Tip: Copy and paste directly into Upwork.") 