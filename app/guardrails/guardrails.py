from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class GuardrailDecision:
    allowed: bool
    reason: str = "allowed"


class InputGuardrails:
    SENSITIVE = [
        re.compile(r"\b(?:password|senha)\s*[:=]\s*\S+", re.I),
        re.compile(r"\b(?:token|api[_ -]?key)\s*[:=]\s*\S+", re.I),
    ]
    INJECTION = [
        re.compile(r"ignore (?:all|any|the) previous instructions", re.I),
        re.compile(r"reveal (?:your|the) system prompt", re.I),
    ]

    def check(self, message: str) -> GuardrailDecision:
        for pattern in self.SENSITIVE:
            if pattern.search(message):
                return GuardrailDecision(False, "Potential secret detected. Remove credentials before sending the request.")
        for pattern in self.INJECTION:
            if pattern.search(message):
                return GuardrailDecision(False, "Prompt-injection style instruction detected and blocked.")
        return GuardrailDecision(True)
