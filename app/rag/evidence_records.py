"""Source-associated passages; product scope is conservative metadata, not entailment."""
import hashlib
import re
from urllib.parse import urlparse
from pydantic import BaseModel, ConfigDict
from app.orchestration.intents import products, normalized

class EvidenceRecord(BaseModel):
    model_config = ConfigDict(extra='forbid')
    text: str
    product: str | None = None
    section: str = ''
    source_id: str
    url: str
    source_index: int
    scope_basis: str = 'unconfirmed'


def _names(text):
    names = products(text)
    specific = [name for name in names if name != 'maquininha']
    return specific or names


def build_records(contexts, sources, chunks=None):
    records = []
    chunks = chunks or []
    for i, text in enumerate(contexts):
        source = sources[i] if i < len(sources) else None
        meta = chunks[i].get('metadata', {}) if i < len(chunks) else {}
        section = str(meta.get('section') or '')
        url = source.url if source else ''
        title = source.title if source else ''
        section_names = _names(section)
        # Section scope overrides a page scope, but a mixed section is ambiguous.
        product, basis = None, 'unconfirmed'
        if len(section_names) == 1:
            product, basis = section_names[0], 'section'
        elif not section_names:
            declared = _names(str(meta.get('product', '')).replace('-', ' '))
            page = declared or _names(title + ' ' + urlparse(url).path.replace('-', ' '))
            if len(page) == 1:
                product, basis = page[0], 'page'
                # Do not turn a cross-sell mention into a feature of the page product.
                other = set(_names(text)) - {product, 'antecipação', 'Pix'}
                if other:
                    product, basis = None, 'mixed_product_passage'
        digest = hashlib.sha256((url+'\n'+section+'\n'+text).encode()).hexdigest()[:20]
        records.append(EvidenceRecord(text=text, product=product, section=section,
            source_id=digest, url=url, source_index=i, scope_basis=basis))
    return records


def attach_records(candidates, records):
    lookup = {record.source_index: record for record in records}
    for item in candidates:
        record = lookup.get(item['source_index'])
        if record:
            item.update(product=record.product, section=record.section,
                        source_id=record.source_id, url=record.url, scope_basis=record.scope_basis)
    return candidates


def attribution_question(question):
    q = normalized(question)
    return len(products(question)) > 1 and bool(re.search(
        r'pertenc|funcionalidade|recurso|beneficio|qual.*produto|which.*product|feature|\bou\b|\bor\b', q))


def render_attribution(question, metadata):
    selected = metadata.get('selected_evidence', [])
    if not selected or not any(item.get('source_id') for item in selected):
        return None
    lines = ['Nos trechos selecionados:']
    confirmed = set()
    for item in selected:
        product = item.get('product')
        if product:
            confirmed.add(product)
            lines.append('- **'+product+'**: '+item['text'])
        else:
            lines.append('- **Produto não confirmado neste trecho**: '+item['text'])
    if attribution_question(question):
        missing = [p for p in products(question) if p not in confirmed]
        if missing:
            lines.append('\nNos trechos selecionados, não consegui confirmar essa associação com '+', '.join(missing)+'. Isso não demonstra que esses produtos não ofereçam o recurso.')
    return '\n'.join(lines)

# Lexical focus is intentionally narrow: it never guesses a missing synonym.
_STOP = set('a o as os de da do das dos e ou um uma uns umas em na no nas nos para por com que qual quais esse essa isso esta este se ao aos é e faz faço funcionalidade funcionalidades recurso recursos beneficio beneficios pertence pertencer oferece oferecer tem ter lista listar gratis gratuito'.split())

def focus_tokens(text, question):
    product_words=set()
    for name in products(question):
        product_words.update(re.findall(r'\w+', normalized(name)))
    return set(re.findall(r'\w+', normalized(text))) - _STOP - product_words


def focus_selection(question, candidates, metadata):
    """Reject unrelated extras when an explicit feature phrase has lexical support."""
    if not attribution_question(question):
        return
    query_tokens=focus_tokens(question, question)
    focused={item['id'] for item in candidates if len(focus_tokens(item['text'],question) & query_tokens) >= 2}
    if not focused:
        return
    selected=[item for item in metadata.get('selected_evidence',[]) if item['id'] in focused]
    if not selected:
        from app.services.llm import LLMError
        raise LLMError('Selected spans miss the explicit feature focus')
    metadata['selected_evidence']=selected
    metadata['selected_evidence_ids']=[item['id'] for item in selected]
    metadata['focus_policy']='explicit_lexical_feature'


def verified_attribution(question, result):
    """Verify only a literal feature quotation scoped to one explicit source section.

    This does not prove exclusivity, absence, truth or universal entailment.
    """
    if result.metadata.get('generation_kind') != 'llm_evidence_selection' or not attribution_question(question):
        return False
    q=normalized(question)
    if re.search(r'\b(?:nao|nunca|exclusiv\w*|somente|apenas|unico|unica|so|todos|todas)\b',q):
        return False
    selected=result.metadata.get('selected_evidence',[])
    records=result.metadata.get('evidence_records',[])
    if not selected or not records or render_attribution(question,result.metadata) != result.answer:
        return False
    lookup={record.get('source_id'):record for record in records}
    squash=lambda text: re.sub(r'\s+',' ',text).strip()
    for item in selected:
        record=lookup.get(item.get('source_id'))
        if not record or record.get('scope_basis')!='section' or _names(record.get('section','')) != [item.get('product')]:
            return False
        if len(focus_tokens(item['text'],question))<2 or normalized(item['text']) not in q:
            return False
        if item.get('product') not in products(question):
            return False
        if any(item.get(key)!=record.get(key) for key in ('product','section','source_index','url','scope_basis')):
            return False
        index=item.get('source_index')
        if type(index) is not int or not 0<=index<len(result.sources):
            return False
        source=result.sources[index]
        if source.url!=record['url'] or squash(record['text']) not in squash(source.snippet) or squash(item['text']) not in squash(record['text']):
            return False
        digest=hashlib.sha256((record['url']+'\n'+record['section']+'\n'+record['text']).encode()).hexdigest()[:20]
        if digest!=record['source_id']:
            return False
    return True


def unsupported_label_relation(answer, records, question):
    """Narrow guard: a quoted feature label must not explain another source fact.

    Detects the observed colon-style conflation, not arbitrary paraphrase entailment.
    """
    facts=[]
    for record in records or []:
        for line in record.text.splitlines():
            fact=line.strip()
            if len(focus_tokens(fact,question))>=2:
                facts.append(fact)
    for line in answer.splitlines():
        if ':' not in line:
            continue
        cleaned=re.sub(r'^\s*\d+[.)]\s*','',line.replace('*','')).strip()
        label, explanation=cleaned.split(':',1)
        if not any(normalized(label.strip())==normalized(fact) for fact in facts):
            continue
        if any(normalized(cleaned) in normalized(record.text) for record in records or []):
            continue
        for fact in facts:
            if normalized(fact)!=normalized(label.strip()) and len(focus_tokens(fact,question) & focus_tokens(explanation,question))>=2:
                return True
    return False
