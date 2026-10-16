from __future__ import annotations

import re
import time
from urllib.parse import urlparse
from app.rag.relevance import relevant, signup_evidence, answer_abstains, policy_question, policy_evidence, unsupported_features, unsupported_relations, catalog_question, catalog_from_evidence
from app.rag.evidence_selection import select_evidence
from app.rag.answer_policy import commercial_excerpts, pix_modalities, unsupported_critical_claims, missing_current_measurement, pricing_question, money_claim, procedure_excerpt
from app.orchestration.intents import signup
from dataclasses import dataclass
from app.agents.base import AgentResult
from app.services.llm import LLMClient, LLMError, LLMTruncatedError
from app.tools.rag_search import RAGSearchTool
from app.tools.web_search import WebSearchTool


@dataclass
class EvidenceKnowledgeAgent:
    rag: RAGSearchTool
    web: WebSearchTool
    llm: LLMClient
    llm_enabled: bool = False

    CORPORATE_HINTS = re.compile(r"getnet|get smart|get cl[aá]ssica|(?:link (?:de )?pagamento|payment link)|credi[aá]rio|antecip|maquininha|pix|conta digital|get conta|digital account|get tap", re.I)
    CURRENT_HINTS = re.compile(r"today|tomorrow|hoje|amanh[aã]|weather|forecast|clima|tempo|exchange rate|c[aâ]mbio|euro|d[oó]lar", re.I)

    def _answer_from_context(self, question: str, contexts: list[str], records=None) -> tuple[str, dict]:
        context = "\n\n".join(contexts)[:10000]
        if signup(question) and not signup_evidence(context):
            return ("Os trechos disponíveis explicam o uso, mas não confirmam a contratação desta solução. Consulte a fonte oficial ou o atendimento humano.",
                    {"generation_kind":"validation_abstention","abstained":True,"grounding_status":"no_signup_evidence","fallback":"signup_evidence_missing"})
        if policy_question(question) and not policy_evidence(question, contexts):
            return ("Não encontrei evidência explícita para confirmar essa condição nas fontes consultadas.",
                    {"generation_kind":"validation_abstention","abstained":True,"fallback":"policy_evidence_missing","grounding_status":"insufficient_evidence"})
        if catalog_question(question):
            catalog = catalog_from_evidence(contexts)
            if catalog:
                return ("Nos trechos consultados aparecem estas soluções: " + ", ".join(catalog) + ".",
                        {"generation_kind":"grounded_catalog_extraction","catalog_scope":"retrieved_sources_only","grounding_status":"source_name_presence"})
        if self.llm_enabled:
            extracted = commercial_excerpts(question, contexts) or pix_modalities(question, contexts) or procedure_excerpt(question, contexts)
            if extracted is not None:
                return extracted
        generation_contexts = contexts
        generation_positions = list(range(len(contexts)))
        if self.llm_enabled and self.CORPORATE_HINTS.search(question) and not pricing_question(question):
            generation_positions = [i for i,text in enumerate(contexts) if not money_claim(text)]
            generation_contexts = [contexts[i] for i in generation_positions]
            if not generation_contexts:
                return ("Os trechos disponíveis trazem condições comerciais, mas não explicam a utilização solicitada.",
                        {"generation_kind":"validation_abstention","abstained":True,"fallback":"only_commercial_context"})
            context = "\n\n".join(generation_contexts)[:10000]
        fallback_reason = "llm_disabled"

        if self.llm_enabled:
            try:
                return select_evidence(self.llm, question, generation_contexts, generation_positions, records=records)
            except LLMTruncatedError:
                return ('A resposta atingiu o limite de saída e não será apresentada como completa.',
                        {'generation_kind': 'llm_truncated', 'abstained': True, 'response_incomplete': True, 'fallback': 'output_limit'})
            except LLMError as exc:
                fallback_reason = type(exc.__cause__).__name__ if exc.__cause__ else type(exc).__name__
        return ('Não consegui gerar uma resposta com o modelo. Trechos recuperados, sem interpretação:\n\n' + '\n\n'.join(contexts[:2]),
                {'generation_kind': 'extractive_fallback', 'generation_fallback': fallback_reason})
