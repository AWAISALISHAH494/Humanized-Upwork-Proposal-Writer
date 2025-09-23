from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


TEMPLATES: Dict[str, Dict[str, str]] = {
	"friendly": {
		"greeting": "Hi there,",
		"closing": "Looking forward to collaborating!",
	},
	"formal": {
		"greeting": "Hello,",
		"closing": "Kind regards,",
	},
	"concise": {
		"greeting": "Hi,",
		"closing": "Regards,",
	},
}


@dataclass
class TemplateManager:
	style: str = "friendly"

	def greeting(self) -> str:
		return TEMPLATES.get(self.style, TEMPLATES["friendly"])['greeting']

	def closing(self) -> str:
		return TEMPLATES.get(self.style, TEMPLATES["friendly"])['closing'] 