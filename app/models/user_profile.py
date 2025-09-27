from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional


class UserProfile(BaseModel):
	name: Optional[str] = Field(default=None, description="User's display name to sign proposals")
	role: Optional[str] = Field(default=None, description="Primary job role/title (e.g., Data Scientist)")
	years_experience: Optional[int] = Field(default=None, ge=0, description="Total years of relevant experience")
	qualifications: Optional[str] = Field(default=None, description="Degrees, certifications, notable achievements")

	def summary(self) -> str:
		parts: list[str] = []
		if self.role:
			parts.append(self.role)
		if self.years_experience is not None:
			parts.append(f"{self.years_experience}+ years experience")
		if self.qualifications:
			parts.append(self.qualifications)
		return ", ".join([p for p in parts if p]) 