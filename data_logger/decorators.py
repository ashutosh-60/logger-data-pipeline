# import logging
# import time
# import uuid
# import functools
# # Import the asynchronous context variables from your lineage module
# from data_logger.lineage import current_run_id, current_task_id, current_upstream_id

# def log_task(task_name: str = None, track_time: bool = True, track_stats: bool = False):
#     """
#     Enterprise-grade parameter-driven decorator.
#     - Preserves native function returns cleanly.
#     - Manages distributed task lineage tracing automatically.
#     - Dynamically uses the decorated function's module logger instead of a fixed name.
#     """
#     def decorator(func):
#         # Default task_name to function name if omitted
#         effective_task_name = task_name if task_name else func.__name__

#         @functools.wraps(func)
#         def wrapper(*args, **kwargs):
#             # Dynamic logger based on function module name
#             logger = logging.getLogger(func.__module__)
#             metadata = {}
            
#             # --- PHASE 4: DISTRIBUTED TRACING & GUID TRACKING ---
#             # 1. Establish a persistent global Batch run_id if it doesn't exist yet
            
#             if not current_run_id.get():
#                 current_run_id.set(f"run-{uuid.uuid4().hex[:8]}")
            

#             # 2. Capture the existing parent task context to build the lineage tree
#             parent_task_id = current_task_id.get()
#             if parent_task_id or parent_task_id == "":
#                 parent_task_id = "root"
#             else:
#                 parent_task_id = current_task_id.get()
            
#             previous_upstream_id = current_upstream_id.get()
#             current_upstream_id.set(parent_task_id)
           

#             # 3. Generate tracking task_id for THIS specific function execution
#             new_task_id = effective_task_name
#             current_task_id.set(new_task_id)

#             print(current_task_id.get())
#             # if not parent_task_id:
#             #     import sys
#             #     sys.exit()


            
#             # --- PHASE 5: RUNTIME TIMING & REF HOOK INJECTION ---
#             # start_time = time.perf_counter() if track_time else None
            
#             # # Inject a clean dictionary reference hook if stats capturing is explicitly toggled
#             # metrics_ref = {}
#             # if track_stats:
#             #     kwargs["metrics_hook"] = metrics_ref
            
#             # logger.info(f"Task '{effective_task_name}' initialized. [TaskID: {new_task_id}, UpstreamID: {parent_task_id or 'root'}]")

#             try:
#                 # 🚀 Run the true operational pipeline data function
#                 result = func(*args, **kwargs)
                
#                 # Compute performance time metrics profile upon successful termination
#                 # if track_time and start_time is not None:
#                 #     duration = time.perf_counter() - start_time
#                 #     metadata["task_timing"] = {
#                 #         "task_name": effective_task_name,
#                 #         "duration_seconds": round(duration, 4)
#                 #     }
                
#                 # # Harvest custom pipeline metrics (either returned ProcessMetrics or written by-reference)
#                 # from data_logger.metrics import ProcessMetrics
#                 # if isinstance(result, ProcessMetrics):
#                 #     metadata["operational_metrics"] = result.to_dict()
#                 # elif track_stats and metrics_ref:
#                 #     metadata["operational_metrics"] = metrics_ref

#                 # # Log completion with the cleanly built metadata payload
#                 # if metadata:
#                 #     logger.info(f"Task '{effective_task_name}' completed successfully.", extra=metadata)
#                 # else:
#                 #     logger.info(f"Task '{effective_task_name}' completed successfully.")
                
#                 # 🛡️ Return the raw, untouched functional payload to downstream processes
#                 return result
                
#             except Exception as e:
#                 logger.error(f"Task '{effective_task_name}' failed at runtime. Error: {str(e)}")
#                 raise e
                
#             finally:
#                 # Context cleanup: Safely roll back tracking state to the parent task scope on exit
#                 current_task_id.set(parent_task_id)
#                 current_upstream_id.set(previous_upstream_id)
                
#         return wrapper
#     return decorator

# def log_task_by_ref(task_name: str, track_time: bool = True, track_stats: bool = False):
#     def decorator(func):
#         @functools.wraps(func)
#         def wrapper(*args, **kwargs):
#             metadata = {}
#             start_time = time.perf_counter() if track_time else None
            
#             # Context injection: look for an explicit tracking dictionary in kwargs
#             # If the developer didn't pass one, create a temporary dictionary reference hook
#             if "log_ctx" not in kwargs:
#                 kwargs["log_ctx"] = {}
                
#             logger.info(f"Task '{task_name}' initialized.")
            
#             try:
#                 # Execute the pipeline step
#                 result = func(*args, **kwargs)
                
#                 # Post-Execution: Harvest the values bound to the tracking context hook
#                 if track_stats and kwargs.get("log_ctx"):
#                     metadata["operational_metrics"] = kwargs["log_ctx"]
                
#                 if track_time and start_time is not None:
#                     duration = time.perf_counter() - start_time
#                     metadata["task_timing"] = {
#                         "task_name": task_name,
#                         "duration_seconds": round(duration, 4)
#                     }
                
#                 if metadata:
#                     logger.info(f"Task '{task_name}' completed successfully.", extra={"metadata": metadata})
#                 else:
#                     logger.info(f"Task '{task_name}' completed successfully.")
                
#                 # Returns standard data unmodified
#                 return result
                
#             except Exception as e:
#                 logger.error(f"Task '{task_name}' failed. Error: {str(e)}")
#                 raise e
#         return wrapper
#     return decorator

import functools
import uuid
from typing import Callable, Any, Optional, Dict
from .lineage import current_task_id, current_upstream_id
from .logger import get_logger
from .metrics import ProcessMetrics

def log_task(
    task_name: Optional[str] = None,
    track_time: bool = True,
    metrics_hook: Optional[Dict[str, Any]] = None
):
    """
    Decorator that auto-generates task GUIDs, handles parent-child upstream lineage,
    and optionally logs execution time or metrics by reference.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # 1. LINEAGE TRANSITION
            parent_id = current_task_id.get() or "root" # Active task becomes parent
            new_task_id = f"task-{uuid.uuid4().hex[:8]}" # Generate fresh task GUID
            
            # Save context tokens for restoring on exit
            token_upstream = current_upstream_id.set(parent_id)
            token_task = current_task_id.set(new_task_id)
            
            logger = get_logger(func.__module__)
            display_name = task_name or func.__name__

            logger.info(f"Starting task: {display_name}")
            
            try:
                # 2. EXECUTE THE ACTUAL DATA FUNCTION
                result = func(*args, **kwargs)
                
                # 3. LOG COMPLETION METRICS IF HOOK IS PROVIDED
                extra_meta = {}
                if metrics_hook:
                    extra_meta["operational_metrics"] = metrics_hook.copy()
                    metrics_hook.clear() # Clear reference container for next run
                elif isinstance(result, ProcessMetrics):
                    extra_meta["operational_metrics"] = result.to_dict()
                
                logger.info(f"Completed task: {display_name}", extra=extra_meta)
                return result
            except Exception as e:
                logger.error(f"Task failed: {display_name}. Error: {str(e)}", exc_info=True)
                raise e
            finally:
                # 4. RESTORE PREVIOUS CONTEXT ON EXIT
                current_upstream_id.reset(token_upstream)
                current_task_id.reset(token_task)

        return wrapper
    return decorator
