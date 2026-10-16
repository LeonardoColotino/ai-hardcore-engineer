"""Necessary evidence checks for network troubleshooting, not a universal verifier."""
import re
from app.orchestration.intents import normalized


def network_guidance_query(question):
    q=normalized(question)
    return bool(re.search(r'maquin|machine|terminal|get smart|get classica',q)) and bool(
        re.search(r'internet|wi-fi|wifi|conexao|connect',q)) and bool(
        re.search(r'indispon|falh|erro|error|nao.*conect|won.?t.*connect|not.*connect|sem.*conex|solucao.*problema|troubleshoot',q))


def actionable_network_span(text):
    t=normalized(text)
    action=re.search(r'\b(?:verifi\w*|confir\w*|reinici\w*|conecte|selecione|pressione|acesse|ativ\w*|desativ\w*|aguarde|aproxime|check|restart|reboot|enable|disable|select|press|open|connect|wait)\b',t)
    technical=re.search(r'\b(?:wi-fi|wifi|internet|rede|network|roteador|router|configura\w*|menu|tecla|terminal|maquina|maquininha|machine|sinal|signal|senha|password|conexao|connection|modem)\b',t)
    return bool(action and technical)


def missing_guidance():
    return ('Não encontrei orientações técnicas documentadas suficientes para esse problema de conexão. Atendimento humano recomendado.',
            {'generation_kind':'validation_abstention','abstained':True,'fallback':'no_evidence','evidence_gap':'technical_guidance_missing'})


def quoted_guidance(contexts, candidates, records=None):
    """Fallback publishes only filtered action spans, never the raw page's ads."""
    from app.rag.evidence_selection import clean_line
    from app.rag.evidence_records import attach_records
    ordered=sorted(candidates,key=lambda item:(item['source_index'],clean_line(contexts[item['source_index']]).find(item['text'])))
    if records:
        attach_records(ordered,records)
    return ('Orientações técnicas nos trechos consultados:\n\n'+'\n'.join('- '+item['text'] for item in ordered)+
            '\n\nTrechos parciais: confira na fonte o procedimento completo e o modelo ao qual se aplica.',
            {'generation_kind':'technical_evidence_extraction','grounding_status':'source_spans_not_complete_procedure',
             'selected_evidence':ordered,'coverage':'partial','outcome':'partial','resolved':False})
