"""Conservative evidence policies for commercial terms and payment modalities.

These policies quote documented text. They do not establish universal entailment.
"""
import re
from app.orchestration.intents import normalized, products


def pricing_question(question):
    return bool(re.search(r'\b(?:taxas?|tarifas?|precos?|custo|custos|fees?|pricing|rates?)\b|quanto custa',normalized(question)))


def money_claim(text):
    return bool(re.search(r'R\$\s*\d|\d+(?:[.,]\d+)?\s*%',text,re.I))


def _distinct(items):
    result=[];seen=set()
    for item in items:
        key=normalized(re.sub(r'\s+',' ',item).strip())
        if key and key not in seen:
            seen.add(key);result.append(item)
    return result


def commercial_excerpts(question, contexts):
    if not pricing_question(question):
        return None
    offers=[text for text in contexts if money_claim(text)]
    if not offers:
        return None
    conditions=[text for text in contexts if re.search(r'condic|sujeit|elegiv|novos clientes|somente para',normalized(text))]
    blocks=_distinct(offers+conditions)
    from .evidence_selection import clean_line
    cleaned=[]
    skip = r'venda online de forma.*pratica.*segura|quero contratar|eu quero|recomendado|leve agora|taxas exclusivas|valor da venda|forma de recebimento|como quer receber|com a getnet.*recebe|taxa unica para compras|confira|nossas taxas'
    for block in blocks:
        lines=[clean_line(line) for line in block.splitlines() if clean_line(line)]
        for i,line in enumerate(lines):
            t=normalized(line)
            if re.search(skip,t) or t in {'por','r$','0',',00','r$ 0 ,00','r$0,00','/mes'}:
                continue
            if t.startswith('simule '):
                cleaned.append('Simulação apresentada na fonte:')
                continue
            if re.fullmatch(r'R\$\s*\d+(?:[.,]\d+)?',line) and i+1<len(lines) and normalized(lines[i+1])=='/mes':
                line += ' '+lines[i+1]
            cleaned.append(line)
    cleaned=_distinct(cleaned)
    if not cleaned or sum(map(len,cleaned))>4500:
        return ('Não consegui preservar as condições comerciais em uma resposta completa. Consulte as fontes ou o atendimento humano.',
                {'generation_kind':'validation_abstention','abstained':True,'fallback':'commercial_context_too_long'})
    return ('Valores e condições nos trechos consultados:\n\n'+'\n'.join(cleaned)+
            '\n\nConfirme na fonte oficial as condições aplicáveis ao seu contrato.',
            {'generation_kind':'commercial_evidence_extraction','grounding_status':'source_excerpts_cleaned_not_personal_quote',
             'commercial_scope':'retrieved_offers_not_personal_quote','evidence_excerpts':blocks,'presented_lines':cleaned})


def pix_modalities(question, contexts):
    if products(question) != ['Pix'] or not re.search(r'como.*funciona|how.*work',normalized(question)):
        return None
    from .evidence_selection import clean_line
    blocks=[];modalities=[];conditions=[]
    for text in contexts:
        lines=[clean_line(line) for line in text.splitlines()]
        start=next((i for i,line in enumerate(lines) if re.search(r'receba com pix atraves de',normalized(line))),None)
        if start is not None:
            end=next((i for i in range(start+1,len(lines)) if re.search(r'quero vender|quero contratar|mais beneficios|horario de recebimento',normalized(lines[i]))),len(lines))
            modalities.extend(re.sub(r'\s+Novo$','',line,flags=re.I) for line in lines[start+1:end] if line)
            # Store the original source, separate from cleaned presentation.
            blocks.append(text)
        for match in re.finditer(r'\*?O hor[aá]rio de recebimento do Pix\b[^.]*\.',text,re.I):
            conditions.append(match.group(0).strip())
            blocks.append(match.group(0).strip())
    modalities=_distinct(modalities);conditions=_distinct(conditions)
    if not modalities:
        return None
    return ('Modalidades descritas na fonte:\n\n'+'\n'.join('- '+line for line in modalities)+
            ('\n\n'+'\n'.join(clean_line(line) for line in conditions) if conditions else ''),
            {'generation_kind':'payment_modalities_extraction','grounding_status':'source_excerpts_cleaned',
             'evidence_excerpts':_distinct(blocks),'presented_lines':modalities})


def procedure_excerpt(question,contexts):
    creating = bool(re.search(r'como.*criar|como.*crio|como.*gerar|how.*create', normalized(question)))
    overview = products(question) == ['Link de Pagamento'] and bool(re.search(r'como.*funciona|how.*work', normalized(question)))
    if not (creating or overview):
        return None
    from .evidence_selection import clean_line,promotional
    for text in contexts:
        t=normalized(text)
        if all(re.search(pattern,t) for pattern in (r'acesse|acessar',r'crie|criar',r'configure|preencha',r'compartilh|copiar')):
            lines=[clean_line(line) for line in text.splitlines()]
            lines=[line for line in lines if line and not promotional(line)]
            return ('Passos documentados na fonte:\n\n'+'\n'.join(lines),
                    {'generation_kind':'procedure_evidence_extraction','grounding_status':'source_procedure_excerpt',
                     'procedure_complete_in_source':True,'evidence_excerpts':[text]})
    return None


def unsupported_critical_claims(question, answer, contexts):
    evidence=normalized(' '.join(contexts));a=normalized(answer)
    issues=[]
    if not pricing_question(question) and money_claim(answer):
        issues.append('unsolicited_commercial_number')
    # Equipment instructions and biometric specifics require the named action
    # or property in source text. Mere product-name overlap is insufficient.
    if set(products(question)) & {'Get Smart','Get Clássica','maquininha','Pix'}:
        for term in ('cancelar','fazer compra','fazer pagamento','impressao digital','envia um qr','instantaneamente'):
            if term in a and term not in evidence:
                issues.append('unsupported:'+term)
    return issues


def missing_current_measurement(question, contexts):
    q=normalized(question)
    if re.search(r'cotacao|cambio|exchange rate',q) and re.search(r'euro|dolar|eur|usd',q):
        # A page saying "quanto vale 1 €" is not an actual measured exchange rate.
        return not any(re.search(r'(?:R\$|BRL)\s*\d+[.,]\d+|\d+[.,]\d+\s*(?:BRL|reais)',text,re.I) for text in contexts)
    if re.search(r'clima|previsao do tempo|weather|forecast',q):
        return not any(re.search(r'\d+\s*°\s*[CF]|\d+\s*(?:graus|mm)',text,re.I) for text in contexts)
    return False
