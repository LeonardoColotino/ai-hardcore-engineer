from __future__ import annotations
from dataclasses import dataclass
from app.models.tools import ToolResult
from app.services.customer_data import JsonRepository, DataAccessError


@dataclass
class CustomerLookupTool:
    repository: JsonRepository
    name: str = "customer_lookup"

    def run(self, user_id: str) -> ToolResult:
        if not user_id.strip():
            return ToolResult(success=False, error="user_id must not be blank")
        try:
            customer = self.repository.customer(user_id)
        except DataAccessError as exc:
            return ToolResult(success=False, error=str(exc))
        if not customer:
            return ToolResult(success=False, error="Customer not found")
        safe = {k: v for k, v in customer.items() if k not in {"password", "token", "secret"}}
        return ToolResult(success=True, data={"customer": safe})
