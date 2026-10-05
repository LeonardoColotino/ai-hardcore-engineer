from __future__ import annotations

import json
import tempfile
from dataclasses import replace
from pathlib import Path

from app.agents.escalation import EscalationAgent
from app.agents.knowledge import KnowledgeAgent
from app.agents.router import RouterAgent
from app.agents.support import SupportAgent
from app.config import get_settings
from app.guardrails.guardrails import InputGuardrails
from app.models.api import ChatRequest
from app.models.tools import SourceItem, ToolResult
from app.orchestration.orchestrator import Orchestrator
from app.rag.ingest import seed_documents
from app.rag.retriever import Retriever
from app.rag.vector_store import NumpyVectorStore
from app.services.customer_data import JsonRepository
from app.services.embeddings import HashingEmbeddingService
from app.services.llm import DisabledLLMClient
from app.tools.customer_lookup import CustomerLookupTool
from app.tools.payment_status import PaymentStatusTool
from app.tools.rag_search import RAGSearchTool
from app.tools.transaction_lookup import TransactionLookupTool

DATASET = Path(__file__).with_name("dataset.json")
PROJECT_DATA = Path(__file__).resolve().parents[1] / "app" / "data"


class StaticWebTool:
    name = "web_search"

    def run(self, query: str) -> ToolResult:
        return ToolResult(
            success=True,
            data={"query": query, "count": 1},
            sources=[SourceItem(title="Offline evaluation web result", url="https://example.test/current", snippet="Offline stub result for deterministic evaluation.")],
        )


def build_orchestrator(index_dir: Path) -> Orchestrator:
    settings = replace(get_settings(), llm_provider="disabled")
    llm = DisabledLLMClient()
    embeddings = HashingEmbeddingService()
    docs = seed_documents()
    store = NumpyVectorStore(index_dir)
    store.build(embeddings.embed([d["text"] for d in docs]), docs)
    retriever = Retriever(store, embeddings, top_k=4, min_score=settings.rag_min_score)
    repo = JsonRepository(PROJECT_DATA)
    return Orchestrator(
        router=RouterAgent(settings, llm),
        knowledge=KnowledgeAgent(RAGSearchTool(retriever), StaticWebTool(), llm, llm_enabled=False),
        support=SupportAgent(CustomerLookupTool(repo), TransactionLookupTool(repo), PaymentStatusTool(repo)),
        escalation=EscalationAgent(),
        guardrails=InputGuardrails(),
    )


def main() -> None:
    cases = json.loads(DATASET.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(prefix="ai-hardcore-eval-") as tmp:
        orchestrator = build_orchestrator(Path(tmp) / "index")
        routing_ok = tool_ok = retrieval_ok = grounding_ok = failure_ok = 0
        retrieval_total = grounding_total = failure_total = 0
        rows = []
        for case in cases:
            response = orchestrator.handle(ChatRequest(message=case["message"], user_id=case["user_id"]))
            route_pass = response.agent == case["expected_agent"]
            tool_pass = case["expected_tool"] is None or response.tool == case["expected_tool"]
            routing_ok += int(route_pass)
            tool_ok += int(tool_pass)

            retrieval_pass = None
            if case.get("expect_sources") is not None:
                retrieval_total += 1
                retrieval_pass = bool(response.sources) == bool(case["expect_sources"])
                retrieval_ok += int(retrieval_pass)

            grounding_pass = None
            if response.sources:
                grounding_total += 1
                snippets = [src.snippet.strip() for src in response.sources if src.snippet.strip()]
                grounding_pass = any(snippet[:80] in response.answer for snippet in snippets) if snippets else False
                grounding_ok += int(grounding_pass)

            failure_pass = None
            if case.get("expect_escalated") is not None:
                failure_total += 1
                failure_pass = response.escalated is bool(case["expect_escalated"])
                failure_ok += int(failure_pass)

            rows.append({
                "id": case["id"],
                "agent": response.agent,
                "expected_agent": case["expected_agent"],
                "tool": response.tool,
                "expected_tool": case["expected_tool"],
                "routing_pass": route_pass,
                "tool_pass": tool_pass,
                "retrieval_pass": retrieval_pass,
                "grounding_pass": grounding_pass,
                "failure_pass": failure_pass,
            })

    total = len(cases)
    report = {
        "total_cases": total,
        "routing_accuracy": round(routing_ok / total, 4),
        "tool_selection_accuracy": round(tool_ok / total, 4),
        "retrieval_source_presence_accuracy": round(retrieval_ok / retrieval_total, 4) if retrieval_total else None,
        "source_excerpt_presence_accuracy": round(grounding_ok / grounding_total, 4) if grounding_total else None,
        "failure_behavior_accuracy": round(failure_ok / failure_total, 4) if failure_total else None,
        "rows": rows,
        "note": "Deterministic offline end-to-end evaluation. Web is stubbed and LLM generation is disabled; Source excerpt presence is not factual grounding or retrieval relevance. Live quality/latency must be validated after Ollama and internet are connected.",
    }
    out = Path(__file__).with_name("report.json")
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "rows"}, indent=2))
    print(f"Detailed report: {out}")
    if any(any(row[key] is False for key in ("routing_pass", "tool_pass", "retrieval_pass", "grounding_pass", "failure_pass")) for row in rows):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
