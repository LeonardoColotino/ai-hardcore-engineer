from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class DataAccessError(RuntimeError):
    pass


@dataclass
class JsonRepository:
    data_dir: Path

    def _load(self, filename: str) -> list[dict[str, Any]]:
        path = self.data_dir / filename
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise DataAccessError(f"Could not access {filename}") from exc
        if not isinstance(payload, list):
            raise DataAccessError(f"Invalid data format in {filename}")
        return payload

    def customer(self, user_id: str) -> dict[str, Any] | None:
        return next((x for x in self._load("customers.json") if x.get("user_id") == user_id), None)

    def transactions(self, user_id: str) -> list[dict[str, Any]]:
        return [x for x in self._load("transactions.json") if x.get("user_id") == user_id]

    def payments(self, user_id: str) -> list[dict[str, Any]]:
        return [x for x in self._load("payments.json") if x.get("user_id") == user_id]
