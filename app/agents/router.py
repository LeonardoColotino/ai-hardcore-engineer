from __future__ import annotations

import re
from dataclasses import dataclass
from app.config import Settings
from app.models.routing import AgentName, RoutingDecision
from app.services.llm import LLMClient, LLMError, parse_json_object


@dataclass
class RouterAgent:
    settings: Settings
    llm: LLMClient

    SUPPORT_PATTERNS = (
        r"\bmy\b.*\b(?:sale|sales|payment|transaction|deposit|deposited|machine|account)\b",
        r"\b(minha|meu|meus|minhas)\b.*\b(vendas?|pagamentos?|transa[cç][aã]o|transa[cç][oõ]es|dep[oó]sitos?|maquin(?:inha|a)?|conta)\b",
        r"\b(?:declin\w*|recusad\w*|erro|not connect|n[aã]o conecta|internet)\b",
        r"\b(?:when will|quando).*\b(?:deposit|deposited|receive|receber|cair|depositad)\b",
    )
    GETNET_PATTERNS = (
        r"\bgetnet\b", r"\bget smart\b", r"\bget cl[aá]ssica\b", r"\b(?:link (?:de )?pagamento|payment link)\b",
        r"\bpix\b", r"\bcredi[aá]rio\b", r"\bantecip(?:a[cç][aã]o|ation)\b", r"\bmaquininha\b", r"\bpix\b.*\b(?:sales|venda|receber|getnet)\b", r"\b(?:sales|venda|receive|receber)\b.*\bpix\b",
    )
    GENERAL_PATTERNS = (
        r"\bweather\b", r"\bforecast\b", r"\bclima\b", r"\btempo\b", r"\bexchange rate\b", r"\bc[aâ]mbio\b", r"\beuro\b", r"\bd[oó]lar\b",
        r"\bcapital of\b", r"\bwhat is the capital\b", r"\bqual (?:é|e) a capital\b",
        r"\bwho is\b", r"\bquem (?:é|e)\b",
    )

    def _matches(self, patterns: tuple[str, ...], text: str) -> int:
        return sum(bool(re.search(p, text, re.I)) for p in patterns)

    def _deterministic(self, message: str) -> RoutingDecision:
        support = self._matches(self.SUPPORT_PATTERNS, message)
        getnet = self._matches(self.GETNET_PATTERNS, message)
        general = self._matches(self.GENERAL_PATTERNS, message)
        product_policy_question = bool(re.search(
            r"\b(?:do i need|can i|how does|how many|what(?:'s| is) the difference|preciso|posso|como funciona|quantas?)\b",
            message,
            re.I,
        ))
        # General product/policy questions must not be mistaken for account lookups merely because they use words like "my sales".
        if getnet >= 1 and product_policy_question:
            return RoutingDecision(agent=AgentName.KNOWLEDGE, reason="General Getnet product/policy question", confidence=min(0.94, 0.78 + 0.05 * getnet))
        # Account-specific evidence otherwise outranks generic product terms.
        if support >= 1:
            confidence = min(0.96, 0.73 + 0.08 * support)
            return RoutingDecision(agent=AgentName.SUPPORT, reason="Request appears account-specific or asks for troubleshooting/settlement data", confidence=confidence)
        if getnet >= 1 or general >= 1:
            confidence = min(0.94, 0.70 + 0.08 * max(getnet, general))
            reason = "Getnet/product knowledge request" if getnet else "General/current-information request"
            return RoutingDecision(agent=AgentName.KNOWLEDGE, reason=reason, confidence=confidence)
        return RoutingDecision(agent=AgentName.ESCALATION, reason="Intent is ambiguous and no safe specialized route reached the confidence threshold", confidence=0.35)

    def route(self, message: str) -> RoutingDecision:
        if self.settings.llm_provider == "ollama":
            system = (
                "You are a routing classifier. Choose exactly one agent: knowledge, support, escalation. "
                "knowledge handles Getnet product knowledge and general/current questions; support handles account-specific customer data, settlements, transactions and machine troubleshooting; escalation handles ambiguous/unsupported requests. "
                "Return ONLY JSON with keys agent, reason, confidence (0..1)."
            )
            try:
                raw = self.llm.generate(system, message)
                obj = parse_json_object(raw)
                decision = RoutingDecision(**obj, source="llm")
                if decision.confidence >= self.settings.router_min_confidence:
                    return decision
            except (LLMError, ValueError, TypeError):
                pass
        decision = self._deterministic(message)
        if decision.confidence < self.settings.router_min_confidence and decision.agent != AgentName.ESCALATION:
            return RoutingDecision(agent=AgentName.ESCALATION, reason="Router confidence below threshold", confidence=decision.confidence, source=decision.source)
        return decision
