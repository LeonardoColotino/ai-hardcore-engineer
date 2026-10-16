"""Server-side outbound query boundary. Fail closed on account/private context."""
import re

class PrivateQueryError(ValueError):
    pass


def public_query(query: str) -> str:
    text = str(query).strip()
    # Never forward free-form support records, credentials, account identifiers or PII.
    private = (
        r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}',
        r'\b\d[\d .()/+-]{6,}\d\b',
        r'\b(?:bearer|password|senha|token|cpf|cnpj|user_id|session_id|account_id)\b',
        r'\b(?:cliente|customer)\s*[-_]?\d+',
        r'\b(?:minh[ao]s? (?:conta|vendas|pagamentos|transa|repasse)|my (?:account|sales|payment))',
        r'\b(?:amount|expected_date|account_status|diagnóstico da conta|conta autenticada)\b',
        r'\b(?:R\$|BRL)\s*\d',
    )
    if not text or len(text) > 800 or any(re.search(p, text, re.I) for p in private):
        raise PrivateQueryError('Consulta pública bloqueada por conter contexto privado ou inválido')
    return re.sub(r'\s+', ' ', text)
