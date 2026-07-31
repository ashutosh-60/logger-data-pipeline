# logger.py – core logger factory with automatic lineage run‑id

import logging
from contextlib import contextmanager
import time
from datetime import datetime

from .config import LoggerConfig
from .formatters import get_json_formatter
from .lineage import LineageFilter, current_run_id, initialize_pipeline_context


def get_logger(name: str, config: LoggerConfig = None) -> logging.Logger:
    """Create a configured logger.

    If ``include_lineage`` is enabled in the supplied ``LoggerConfig`` the
    function will ensure that a ``run_id`` is generated exactly once per Python
    process. This removes the need for callers to manually invoke
    ``initialize_pipeline_context``.
    """

    if config is None:
        config = LoggerConfig()

    # # ---------------------------------------------------------------------
    # # Automatic run‑id provisioning (lineage convenience)
    # # ---------------------------------------------------------------------
    # if config.include_lineage:
    #     # Lazily initialise a run identifier if one does not already exist.
    #     if not current_run_id.get():
    #         initialize_pipeline_context()

    logger = logging.getLogger(name)

    # Clear existing handlers to prevent duplicate logs in interactive sessions.
    if logger.hasHandlers():
        logger.handlers.clear()

    logger.setLevel(logging.INFO)

    # Attach the LineageFilter when lineage tracking is requested.
    if config.include_lineage:
        logger.addFilter(LineageFilter())

    # Build the JSON formatter – can be overridden via ``custom_schema``.
    formatter = get_json_formatter(
        custom_schema=config.custom_schema,
        include_lineage=config.include_lineage,
    )

    if config.enable_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


@contextmanager
def timer_scope(scope_name: str, logger_name: str = "inline_runner"):
    """Context manager to autonomously measure and log execution duration
    for procedural or inline data blocks.
    """
    logger = get_logger(logger_name)
    start_wall = datetime.utcnow().isoformat()
    start_perf = time.perf_counter()
    logger.info(
        f"Started inline block '{scope_name}'.",
        extra={"scope_timing": {"start_time": start_wall}},
    )
    try:
        yield
        end_wall = datetime.utcnow().isoformat()
        duration = time.perf_counter() - start_perf
        logger.info(
            f"Finished inline block '{scope_name}'.",
            extra={
                "scope_timing": {
                    "start_time": start_wall,
                    "end_time": end_wall,
                    "duration_seconds": round(duration, 4),
                }
            },
        )
    except Exception as e:
        end_wall = datetime.utcnow().isoformat()
        duration = time.perf_counter() - start_perf
        logger.error(
            f"Inline block '{scope_name}' failed: {str(e)}",
            extra={
                "scope_timing": {
                    "start_time": start_wall,
                    "end_time": end_wall,
                    "duration_seconds": round(duration, 4),
                }
            },
        )
        raise