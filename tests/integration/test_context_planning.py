"""A product context anchor must not become a new user request."""
from types import SimpleNamespace
import pytest
from app.models.routing import AgentName, RoutingDecision
from app.orchestration.planner import build_plan

class NoPlanning:
    def generate_structured(self, *args):
        raise AssertionError('Single explicit request must preserve its original query')
class Router:
    settings=SimpleNamespace(llm_provider='ollama')
    llm=NoPlanning()
    def _deterministic(self, message):
        return RoutingDecision(agent=AgentName.KNOWLEDGE, reason='Getnet product', confidence=.98)
    def route(self, message):
        return self._deterministic(message)

@pytest.mark.parametrize('message',[
    'Como faço para criar esse link? [Contexto da conversa: Getnet Link de Pagamento]',
    'Como crio isso? [Contexto da conversa: Getnet Link de Pagamento]',
    'Como faço para criar esse link [Contexto da conversa: Getnet Link de Pagamento]',
])
def test_product_anchor_does_not_split_a_single_followup(message):
    plan, origin=build_plan(message, Router())
    assert origin=='single_route'
    assert len(plan.tasks)==1 and plan.tasks[0].agent=='knowledge'
    assert plan.tasks[0].query==message
    assert plan.tasks[0].depends_on is None


def test_actual_mixed_request_is_still_split():
    class MixedRouter(Router):
        settings=SimpleNamespace(llm_provider='disabled')
        def _deterministic(self,message):
            agent=AgentName.SUPPORT if 'minhas vendas' in message.lower() else AgentName.KNOWLEDGE
            return RoutingDecision(agent=agent, reason='test', confidence=.98)
    message='Como criar o Link de Pagamento? Consulte minhas vendas. [Contexto da conversa: Getnet Link de Pagamento]'
    plan, origin=build_plan(message,MixedRouter())
    assert origin=='clause_fallback'
    assert [t.agent for t in plan.tasks]==['knowledge','support']
    assert 'criar' in plan.tasks[0].query
