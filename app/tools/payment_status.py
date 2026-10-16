from __future__ import annotations
from dataclasses import dataclass
from app.models.tools import ToolResult
from app.services.customer_data import JsonRepository, DataAccessError


@dataclass
class PaymentStatusTool:
    repository: JsonRepository
    name: str = "payment_status"

    def run(self, user_id: str) -> ToolResult:
        try:
            rows = self.repository.payments(user_id)
        except DataAccessError as exc:
            return ToolResult(success=False, error=str(exc))
        if not rows:
            return ToolResult(success=False, error="No settlement/payment records found for this user")
        return ToolResult(success=True, data={"payments": rows[:10], "count": len(rows)})
