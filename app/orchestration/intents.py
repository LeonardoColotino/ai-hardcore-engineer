"""Small intent policy, shared by routing and state; never selects an identity."""
import re
import unicodedata


def normalized(text):
    return ''.join(c for c in unicodedata.normalize('NFKD', text.lower()) if not unicodedata.combining(c))

PRODUCTS = (
    ('Link de Pagamento', r'\blink(?: de pagamento)?\b|\bpayment link\b'),
    ('Conta Digital', r'\bconta digital\b|\bget conta\b|\bdigital account\b'),
    ('Pix', r'\bpix\b'),
    ('Get Tap', r'\bget tap\b'),
    ('Get Smart', r'\bget smart\b'),
    ('Get Clássica', r'\bget classica\b'),
    ('crediário', r'\bcrediario\b'),
    ('antecipação', r'\bantecipacao\b|\breceivables advance\b'),
    ('maquininha', r'\bmaquin(?:inha|a)s?\b|\bcard machines?\b'),
)


def products(text):
    found = [name for name, pattern in PRODUCTS if re.search(pattern, normalized(text))]
    if any(x in found for x in ('Get Smart', 'Get Clássica')) and 'maquininha' in found:
        found.remove('maquininha')
    return found


def human_request(text):
    t = normalized(text)
    if re.search(r"\bnao\s+(?:quero|preciso).*?(?:humano|atendente|operador)", t):
        return False
    return bool(re.search(
        r"\b(?:quero|preciso|gostaria|chame|chamar|falar|transfira|transferir|want|need|talk|transfer|speak)\b.*?\b(?:humano|humana|atendente|operador|human|operator)\b|\b(?:human|operator) please\b", t))


def social_message(text):
    return bool(re.fullmatch(r"(?:muito )?(?:obrigad[oa]|valeu|thanks|thank you|ok|certo|bom dia|boa tarde|boa noite)[!.,\s]*", normalized(text).strip()))


def account_followup(text):
    t = normalized(text)
    return bool(re.search(r"\b(?:deposito|previsao|prazo|quando|status|essa transacao|essa venda)\b", t)) and not products(text)


def comparison(text):
    return bool(re.search(r"\b(?:das duas|dos dois|ambas|ambos|entre elas|entre eles|which of (?:the )?two|both)\b", normalized(text)))


def reference(text):
    t = normalized(text)
    return bool(re.search(r'\b(?:ess[ae]|est[ae]|aquele|aquela|isso|isto|dela|dele|ela|ele|that|this|it|the latter|a anterior)\b', t)) or bool(re.search(r'^\s*(?:e\s+)?(?:como|how)\s+(?:faco para\s+)?(?:contratar|aderir|criar|usar|create|subscribe|use)\s*\??$', t))


def signup(text):
    return bool(re.search(r'\b(?:contratar|contratacao|aderir|adesao|subscribe|sign up|signup|hire)\b', normalized(text)))


def settlement(text):
    return bool(re.search(r'\b(?:deposit\w*|settlement|dep[oó]sit\w*|ca[ií]r|ca[ií]ram|receb\w*|cair\w*)\b', text, re.I)) and bool(re.search(r'\b(?:my|meu|minha|meus|minhas|vendas?|sales|dinheiro|money|pagamentos?)\b', text, re.I))


def troubleshooting(text):
    t=normalized(text)
    return bool(re.search(r'maquin|machine|terminal', t)) and bool(re.search(r'conect|connect|internet|erro|error|recus|declin|falh|nao funciona|not work',t))
