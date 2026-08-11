from .logger import get_logger, timer_scope
from .config import LoggerConfig
from .metrics import ProcessMetrics
from .decorators import log_task
from .lineage import initialize_pipeline_context, set_pipeline_run_id, LineageFilter
from .handlers.pipeline_hooks import flush_logs

# Explicitly define the public footprint of the pip package
__all__ = [
    "get_logger",
    "timer_scope",
    "LoggerConfig",
    "ProcessMetrics",
    "log_task",
    "initialize_pipeline_context",
    "set_pipeline_run_id",
    "LineageFilter",
    "flush_logs"
]

__version__ = "1.0.0"
