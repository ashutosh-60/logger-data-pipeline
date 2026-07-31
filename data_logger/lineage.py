import contextvars
import uuid
from logging import Filter, LogRecord
from typing import Optional

# Initialize context variables for tracing global state
# A unique tracking string that anchors the entire pipeline run
current_run_id: contextvars.ContextVar[str] = contextvars.ContextVar("current_run_id", default="")
# The identifier of the operational task that triggered this step
current_upstream_id: contextvars.ContextVar[str] = contextvars.ContextVar("current_upstream_id", default="")
# The identifier of the specific active block running
current_task_id: contextvars.ContextVar[str] = contextvars.ContextVar("current_task_id", default="")

def initialize_pipeline_context(run_id: Optional[str] = None) -> str:
    """Initializes the top-level execution run ID, generating a GUID by default."""
    rid = run_id if run_id else str(uuid.uuid4())
    current_run_id.set(rid)
    return rid

class LineageFilter(Filter):
    """
    Autonomously injects distributed tracing metrics into the logging record metadata.
    If explicit contextvars (from decorators) are not set, task_id and upstream_id
    are auto-derived from the execution call-site (record.funcName / record.module).
    """
    def filter(self, record: LogRecord) -> bool:
        # # 1. run_id: set globally or via get_logger auto-provisioning
        # record.run_id = current_run_id.get()
        
        # # 2. task_id: use explicit decorator context if present, otherwise auto-infer from function name
        # explicit_task = current_task_id.get()
        # if explicit_task:
        #     record.task_id = explicit_task
        # else:
        #     # Fallback to function name if inside a function, or module name if at top-level
        #     func = getattr(record, "funcName", "")
        #     if func and func != "<module>":
        #         record.task_id = func
        #     else:
        #         record.task_id = getattr(record, "module", "main")
                
        # # 3. upstream_id: use explicit parent context if present, otherwise default to 'root'
        # explicit_upstream = current_upstream_id.get()
        # if explicit_upstream:
        #     record.upstream_id = explicit_upstream
        # else:
        #     record.upstream_id = "root"
            
        # return True


        record.run_id = current_run_id.get()
        record.upstream_id = current_upstream_id.get()
        record.task_id = current_task_id.get()
        return True