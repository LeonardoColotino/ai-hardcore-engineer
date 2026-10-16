"""Per-request network budget, restored with ContextVar tokens by supervisor."""
from contextvars import ContextVar
import time
request_deadline = ContextVar('request_deadline', default=None)

def timeout(configured):
    deadline = request_deadline.get()
    if deadline is None:
        return max(.1, float(configured))
    remaining = deadline-time.monotonic()
    if remaining <= 0:
        import requests
        raise requests.Timeout('Total chat request budget exhausted')
    # Reserve response/persistence time. requests timeout bounds socket inactivity;
    # an absolute deadline is checked between stages, not a hard cancellation timer.
    return min(float(configured), max(.1, remaining-.5))
