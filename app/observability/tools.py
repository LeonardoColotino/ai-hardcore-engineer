"""Bounded tool telemetry; no queries, account data or credentials in logs."""
import functools, logging, threading, time
from app.observability.logging import log_event
lock=threading.Lock()
failures={}
def instrument(tool):
    original=tool.run
    @functools.wraps(original)
    def run(*args,**kwargs):
        start=time.perf_counter()
        try:
            result=original(*args,**kwargs)
        except Exception as exc:
            with lock: failures[tool.name]=failures.get(tool.name,0)+1
            log_event(logging.getLogger(__name__),'tool_failed',tool=tool.name,error_type=type(exc).__name__,duration_ms=round((time.perf_counter()-start)*1000,2))
            raise
        if not result.success:
            with lock: failures[tool.name]=failures.get(tool.name,0)+1
        log_event(logging.getLogger(__name__),'tool_completed',tool=tool.name,success=result.success,duration_ms=round((time.perf_counter()-start)*1000,2))
        return result
    tool.run=run
    return tool
