"""Bounded V3 supervisor: persistent context, specialist dataflow and handoff."""
import hashlib, logging, os, re, threading, time, uuid
from app.services.budget import request_deadline
from fastapi import HTTPException
from app.persistence import Store
from app.models.api import ChatRequest
from app.observability.logging import log_event, trace_context
locks=[threading.Lock() for _ in range(64)]
rate_lock=threading.Lock()
rates={}
metrics={'requests':0,'escalations':0,'fallbacks':0,'duration_ms_total':0,'errors':0,'answered':0,'abstentions':0,'clarifications':0,'llm_answers_unreviewed':0}
latency_samples=[]

def limit(key):
    with rate_lock:
        now=time.monotonic()
        old=[x for x in rates.get(key,[]) if now-x<60]
        if len(old)>=30: raise HTTPException(429,'Limite de 30 requisições por minuto')
        rates[key]=old+[now]


class Supervisor:
    def handle(self, payload, who, orch):
        limit(who['sub'])
        if payload.user_id is not None and payload.user_id != who['sub']:
            raise HTTPException(403, 'Identidade incompatível')
        store = Store()
        sid = payload.session_id or store.session(who['sub'])['session_id']
        store.check(sid, who['sub'])
        lock = locks[int(hashlib.sha256(sid.encode()).hexdigest(), 16) % len(locks)]
        budget_s=max(1,float(os.getenv("CHAT_BUDGET_S","60")))
        queued=time.monotonic()
        if not lock.acquire(timeout=budget_s):
            raise HTTPException(503, 'Prazo esgotado aguardando a sessão')
        try:
            start = time.perf_counter()
            request_id = 'req-' + uuid.uuid4().hex[:12]
            token = trace_context.set({'request_id':request_id,'session_id':sid,'user_hash':hashlib.sha256(who['sub'].encode()).hexdigest()[:12]})
            budget_token = request_deadline.set(queued+budget_s)
            from app.services.llm import provider_usage
            usage_token = provider_usage.set(None)
            try:
                return self._turn(payload, who, orch, store, sid, start, request_id)
            except Exception:
                with rate_lock:
                    metrics['errors'] += 1
                raise
            finally:
                provider_usage.reset(usage_token)
                request_deadline.reset(budget_token)
                trace_context.reset(token)
        finally:
            lock.release()

    def _turn(self, payload, who, orch, store, sid, start, request_id):
        from app.orchestration.intents import products, reference, troubleshooting, human_request, social_message, account_followup, comparison
        history = store.messages(sid, who['sub'])[-12:]
        state = store.state(sid, who['sub'])
        message = payload.message.strip()
        if len(message) < 2:
            raise HTTPException(422, 'Mensagem vazia')
        guard = orch.guardrails.check(message)
        store.add(sid, 'user', message if guard.allowed else '[Mensagem bloqueada pelo guardrail]')
        agents, stages, ticket_id = [], [], None
        current = products(message)
        is_reference = reference(message)
        candidates = state.get('candidates', [])
        selected = state.get('selected_product')
        result = None
        active_ticket = store.active_ticket(sid, who['sub'])
        if active_ticket:
            result = {'agent':'escalation', 'answer':'Seu atendimento humano está em andamento. Sua mensagem foi registrada para o operador.', 'sources':[], 'escalated':True, 'tool':'human_handoff', 'metadata':{'routing_reason':'human_active','outcome':'awaiting_human'}}
            agents = ['escalation']
        visited = state.get('visited_products', [])
        last_account_tool = state.get('last_account_tool')
        from app.orchestration.intents import topic_reset, settlement
        public_topic = bool(orch.router._matches(orch.router.GENERAL_PATTERNS, message)) if hasattr(orch.router, '_matches') else False
        if topic_reset(message) or (public_topic and not current and not is_reference):
            candidates, selected, visited, last_account_tool = [], None, [], None
        elif settlement(message) and not current:
            # An explicit account subject replaces an earlier product anchor.
            candidates, selected = [], None
        if result is None and guard.allowed and social_message(message):
            result = {'agent':'router','answer':'Por nada! Se precisar, podemos continuar a conversa.', 'sources':[], 'escalated':False,'metadata':{'routing_reason':'social_acknowledgement','outcome':'acknowledged'},'tool':None}
            agents = ['router']
        if guard.allowed and not current and not is_reference and account_followup(message) and last_account_tool:
            if last_account_tool == 'payment_status':
                message += ' [Contexto: minhas vendas e depósito da conta autenticada]'
            elif last_account_tool == 'transaction_lookup':
                message += ' [Contexto: minha transação da conta autenticada]'
        compare_products = visited[-2:] if comparison(message) else []
        # Explicit entities/corrections select a new topic. Implicit references consume persisted state.
        if guard.allowed and len(compare_products) == 2:
            candidates, selected = compare_products, None
            message += ' [Comparação Getnet: '+', '.join(compare_products)+']'
        elif guard.allowed and current:
            last_account_tool = None
            visited = [x for x in visited if x not in current] + current
            candidates = current
            selected = current[0] if len(current) == 1 else None
            if is_reference and selected:
                message += " [Contexto da conversa: Getnet "+selected+"]"
        elif guard.allowed and is_reference and result is None:
            if not selected:
                choices = ', '.join(candidates) if candidates else 'o nome do produto que deseja consultar'
                result = {'agent':'router','answer':'Você se refere a qual solução? Informe '+choices+'.','sources':[],'escalated':False,'metadata':{'routing_reason':'ambiguous_reference','outcome':'clarification'},'tool':None}
                agents = ['router']
            else:
                message += ' [Contexto da conversa: Getnet '+selected+']'
        if result is None and selected and not current and not is_reference and re.search(r'precis|necess|obrig|quem compra|oferece', message, re.I):
            message += ' [Contexto da conversa: Getnet '+selected+']'
        if result is None:
            from app.orchestration.planner import execute_plan
            if not guard.allowed:
                response = orch.handle(ChatRequest(message=message,user_id=who['sub']))
                result = response.model_dump()
                agents = ['escalation']
            else:
                result, agents, stages = execute_plan(message, who['sub'], orch, sid)
        if result['escalated']:
            ticket_id = store.ticket(sid,who['sub'],result['metadata'].get('handoff_reason') or result['metadata'].get('routing_reason','human_review'))
            # Only after SQLite commit may the response claim OPEN/created.
            ticket_status = store.get_ticket(ticket_id, who)['status']
            result['metadata'].update(ticket_created=True,handoff_status=ticket_status,ticket_id=ticket_id,outcome='escalated',resolved=False)
            result['answer'] += '\nAtendimento humano solicitado. Protocolo: '+ticket_id
            if not agents or agents[-1] != 'escalation':
                agents.append('escalation')
                stages.append({'agent':'escalation','duration_ms':0.0,'tool':'human_handoff'})
            result['tool'] = 'human_handoff'
            result['agent'] = 'escalation'
        else:
            result['metadata'].setdefault('outcome','answered' if result['metadata'].get('generation_kind') != 'extractive_fallback' else 'fallback')
            result['metadata']['resolved'] = result['metadata']['outcome'] == 'answered'
            # Presented candidates derive from actual response text rather than a fabricated catalog.
            presented = products(result['answer'])
            if not selected and not current and not compare_products and len(presented) > 1:
                candidates, selected = presented, None
        duration = round((time.perf_counter()-start)*1000,2)
        if result.get('tool') in ('payment_status','transaction_lookup'):
            last_account_tool = result['tool']
        state.update(visited_products=visited[-8:],last_account_tool=last_account_tool,selected_product=selected,candidates=candidates,intent=result['metadata'].get('routing_reason'),stage=result['metadata'].get('outcome'),last_ticket=ticket_id or state.get('last_ticket'))
        store.save_state(sid, who['sub'], state)
        result.update(request_id=request_id,session_id=sid,ticket_id=ticket_id)
        from app.services.llm import get_provider_usage
        result['metadata']['provider_usage'] = get_provider_usage()
        result['metadata']['prompt_version'] = 'planner-1/knowledge-2'
        result['metadata'].update(agents=agents,products=candidates,conversation_state=state,context_messages=len(history),duration_ms=duration,stages=stages)
        store.add(sid,'assistant',result['answer'],{**result['metadata'],'request_id':request_id,'sources':result['sources'],'ticket_id':ticket_id})
        with rate_lock:
            metrics['requests'] += 1
            metrics['escalations'] += int(result['escalated'])
            metrics['fallbacks'] += int(bool(result['metadata'].get('fallback') or result['metadata'].get('generation_fallback')))
            metrics['duration_ms_total'] += duration
            metrics['answered'] += int(result['metadata'].get('outcome') == 'answered')
            metrics['abstentions'] += int(bool(result['metadata'].get('abstained') or result['metadata'].get('fallback') == 'no_evidence'))
            metrics['clarifications'] += int(result['metadata'].get('outcome') == 'clarification')
            metrics['llm_answers_unreviewed'] += int(result['metadata'].get('generation_kind') == 'llm' and not result['escalated'])
            latency_samples.append(duration)
            del latency_samples[:-1000]
        log_event(logging.getLogger(__name__),'session_completed',request_id=request_id,session_id=sid,agents=agents,stages=stages,duration_ms=duration,ticket_id=ticket_id,outcome=result['metadata'].get('outcome'),generation_kind=result['metadata'].get('generation_kind'),routing_reason=result['metadata'].get('routing_reason'),sources=[s.get('url') for s in result['sources']])
        return result
