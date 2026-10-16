"""Read-only synthetic terminal diagnostics; no private identifiers in public context."""
from dataclasses import dataclass
from app.models.tools import ToolResult
from app.services.customer_data import JsonRepository

@dataclass
class TerminalDiagnosisTool:
    repository: JsonRepository
    name: str = 'terminal_diagnosis'

    def run(self, user_id: str) -> ToolResult:
        # Fixture intentionally represents demo telemetry, not a live terminal service.
        customer = self.repository.customer(user_id)
        if not customer:
            return ToolResult(success=False, error='Customer not found')
        return ToolResult(success=True, data={'model':'maquininha', 'connectivity':'Wi-Fi',
            'symptom':'sem conexão com a internet', 'diagnostic_code':'NETWORK_UNAVAILABLE'},
            metadata={'synthetic':True, 'source':'fixed_demo_telemetry'})


def public_diagnosis(data: dict) -> str:
    # Enum mappings prevent arbitrary records or model-provided text reaching retrieval/web.
    model = {'maquininha':'maquininha', 'Get Smart':'Get Smart'}.get(data.get('model'), 'maquininha')
    symptom = {'NETWORK_UNAVAILABLE':'conexão Wi-Fi indisponível',
               'TRANSACTION_DECLINED':'transação recusada'}.get(data.get('diagnostic_code'), 'diagnóstico indisponível')
    return f'Getnet {model}: {symptom}. Orientação oficial de solução do problema.'
