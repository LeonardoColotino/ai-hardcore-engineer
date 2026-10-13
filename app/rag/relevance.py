"""Conservative product/evidence gates; never a universal factual verifier."""
import re
from urllib.parse import urlparse
from app.orchestration.intents import normalized, products, troubleshooting


def relevant(question, text, title='', url=''):
    q, body = normalized(question), normalized(text)
    if troubleshooting(question) or ('maquin' in q and ('conexao' in q or 'internet' in q)):
        primary = products(title + ' ' + urlparse(url).path.replace('-', ' '))
        if primary and not set(primary) & {'maquininha','Get Smart','Get Clássica'}:
            return False
        return bool(re.search(r'maquin|card machine|terminal|get smart|get classica', body + ' ' + normalized(title))) and bool(re.search(r'wi-fi|wifi|internet|conexao|connection|dados moveis|mobile data|rede (?:de dados|sem fio)|network (?:connection|error)', body))
    requested = products(question)
    if not requested:
        return True
    path = normalized(urlparse(url).path).replace('-', ' ')
    primary = products(title + ' ' + path)
    # URLs describe a product; cross-sell mentions are not its specification.
    recognized = set(primary) & {'Pix','Link de Pagamento','Conta Digital','Get Smart','Get Clássica','Get Tap','crediário','antecipação'}
    if recognized and not set(requested) & recognized and not set(requested) & {'antecipação','crediário'}:
        return False
    aliases = {
        'Link de Pagamento':r'link(?: de pagamento)?|payment link|get link',
        'Conta Digital':r'conta digital|get conta|digital account',
        'Get Smart':r'get smart', 'Get Clássica':r'get classica',
        'Get Tap':r'get tap','Pix':r'\bpix\b',
        'crediário':r'crediario','antecipação':r'antecipacao|receivables advance',
        'maquininha':r'maquin|card machine|terminal',
    }
    return bool(set(requested) & recognized) or any(re.search(aliases[p], body) for p in requested)


def signup_evidence(text):
    sentences = re.split(r'[.!?;\n]+', normalized(text))
    return any(re.search(r'\b(?:para contratar|como contratar|contrate|aderir|adesao|sign up|subscribe)\b', s)
               and re.search(r'\b(?:acesse|acessar|entre|solicite|preencha|cadastre|telefone|central|site|aplicativo|app|portal|contact|visit|register|form)\b', s)
               for s in sentences)


def policy_question(question):
    q=normalized(question)
    return bool(re.search(r'\b(?:precis[ao]|necessari\w*|obrigatori\w*|requisito|exclusiv\w*)\b',q)) or bool(re.search(r'oferece.*?(?:cartao virtual|antecipacao)|garant\w*.*?(?:lucro|rendimento)',q))


def policy_evidence(question, contexts):
    q=normalized(question)
    text=normalized(' '.join(contexts))
    if 'conta' in q and re.search(r'precis|necessari|obrigatori|requisit',q):
        return bool(re.search(r'(?:precisa|necessari\w*|obrigatori\w*|nao precisa|dispensa).*?\bconta\b|\bconta\b.*?(?:necessari\w*|obrigatori\w*)', text))
    if 'cartao virtual' in q:
        return 'cartao virtual' in text
    if 'lucro' in q or 'rendimento' in q:
        return bool(re.search(r'lucro|rendimento',text))
    return bool(re.search(r'precis|necessari|obrigatori|requisit|exclusiv',text))


def answer_abstains(answer):
    t=normalized(answer)
    return bool(re.search(
        r'nao (?:tenho|ha|encontrei|consigo|posso|consegui|foi possivel|e possivel).*?(?:informac|evidenc|confirm|encontr)|'
        r'(?:contexto|fontes|trechos|documentos|snippets).*?nao (?:fornece|fornecem|contem|explica|explicam)|'
        r'(?:nao ha|nao tenho).*?(?:cotacao|previsao|valor|taxa)|'
        r'nao (?:esta|estao|consta|constam).*?(?:disponiv|fontes|trechos|contexto)|'
        r'nao (?:e possivel|posso|consigo).*?(?:fornecer|obter|informar).*?(?:cotacao|previsao|valor)|'
        r'(?:informacao|cotacao|previsao|valor).*?(?:indisponivel|nao disponivel)|'
        r'could not find|insufficient evidence|no information|cannot confirm',t,re.S))


def unsupported_features(answer, contexts):
    # Explicit sensitive features may not appear without matching source terms.
    evidence=normalized(' '.join(contexts)); answer=normalized(answer)
    features=['biometria','cartao virtual','antecipacao','conta obrigatoria','atualiza o status do pedido']
    return [feature for feature in features if feature in answer and feature not in evidence]


def unsupported_relations(answer, contexts):
    """Narrow cross-sell guard, not a general entailment judge."""
    a = normalized(answer)
    if 'pix' not in a or 'get tap' not in a:
        return False
    # Require one source line explicitly relating both, rather than a catalog.
    return not any('pix' in normalized(line) and 'get tap' in normalized(line)
                   and re.search(r'aceit|pagamento|receb|pagar|payment', normalized(line))
                   for context in contexts for line in re.split(r'[\n.!?;]+', context))


def catalog_question(question):
    return bool(re.search(r'(?:quais|que|what).*?(?:solucoes|produtos|solutions|products)',normalized(question)))


def catalog_from_evidence(contexts):
    # Enumerate only recognized product names actually present in source text.
    catalog = {'Link de Pagamento','Conta Digital','Pix','Get Tap','Get Smart','Get Clássica','maquininha'}
    found = []
    for context in contexts:
        for name in products(context):
            if name in catalog and name not in found:
                found.append(name)
    return found
