import json
import logging
import pytest
from unittest.mock import MagicMock

from data_logger.config import LoggerConfig
from data_logger.formatters import get_json_formatter
from data_logger.logger import get_logger
from data_logger.lineage import (
    initialize_pipeline_context,
    current_run_id,
    current_task_id,
    current_upstream_id
)
from data_logger.metrics import ProcessMetrics
from data_logger.decorators import log_task

# -------------------------------------------------------------------------
# FIXTURES
# -------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def reset_contextvars():
    """Safely resets lineage context tokens before and after every single test run."""
    token_run = current_run_id.set("")
    token_task = current_task_id.set("")
    token_upstream = current_upstream_id.set("")
    yield
    current_run_id.reset(token_run)
    current_task_id.reset(token_task)
    current_upstream_id.reset(token_upstream)


# -------------------------------------------------------------------------
# PHASE 5: TEST DYNAMIC SCHEMAS (LIST LOOP REFACTOR)
# -------------------------------------------------------------------------
def test_dynamic_formatter_loop_inclusion():
    """Verify that lineage attributes are included in the schema array by default."""
    formatter = get_json_formatter(include_lineage=True)
    
    # Create an active record containing simulated context keys
    logger = logging.getLogger("test_lineage_formatter")
    record = logger.makeRecord(
        name=logger.name, level=logging.INFO, fn="job.py", lno=12,
        msg="Testing loop layout", args=(), exc_info=None
    )
    record.run_id = "run-123"
    record.task_id = "task-456"
    record.upstream_id = "upstream-789"
    
    log_data = json.loads(formatter.format(record))
    
    # Assert that all keys processed by the dynamic list loop exist
    assert "run_id" in log_data
    assert log_data["run_id"] == "run-123"
    assert log_data["task_id"] == "task-456"
    assert log_data["upstream_id"] == "upstream-789"


def test_dynamic_formatter_loop_exclusion():
    """Verify that setting include_lineage=False drops the tracing tokens completely."""
    formatter = get_json_formatter(include_lineage=False)
    
    logger = logging.getLogger("test_clean_formatter")
    record = logger.makeRecord(
        name=logger.name, level=logging.INFO, fn="job.py", lno=12,
        msg="Testing clean layout", args=(), exc_info=None
    )
    
    log_data = json.loads(formatter.format(record))
    
    # Trace elements should be fully absent from the output JSON properties
    assert "run_id" not in log_data
    assert "task_id" not in log_data
    assert "upstream_id" not in log_data
    assert log_data["message"] == "Testing clean layout"


# -------------------------------------------------------------------------
# PHASE 4: TEST DISTRIBUTED TRACING & DECORATORS
# -------------------------------------------------------------------------
def test_pipeline_context_initialization():
    """Verify that initialize_pipeline_context provisions explicit or auto-generated UUID runs."""
    # Test custom string assignment (e.g., Airflow DAG run ID)
    custom_run = initialize_pipeline_context(run_id="airflow_dag_run_abc")
    assert current_run_id.get() == "airflow_dag_run_abc"
    
    # Test automatic fallback provision
    auto_run = initialize_pipeline_context(run_id=None)
    assert len(auto_run) == 36  # Standard GUID length verification


def test_decorator_establishes_lineage_tree():
    """Verify that nested @log_task layers dynamically establish upstream/downstream parent links."""
    initialize_pipeline_context(run_id="execution_root")

    @log_task("parent_job")
    def parent_function():
        parent_id = current_task_id.get()
        assert current_upstream_id.get() == ""  # Root step has no parent
        
        @log_task("child_job")
        def child_function():
            assert current_upstream_id.get() == parent_id  # Downstream correctly links upstream
            assert current_task_id.get() != parent_id  # Child gets its own unique ID
            
        child_function()
        
        # Verify context reverts when child terminates
        assert current_task_id.get() == parent_id
        assert current_upstream_id.get() == ""

    parent_function()


# -------------------------------------------------------------------------
# PHASE 5: TEST OPERATIONAL METRICS CONTRACT
# -------------------------------------------------------------------------
def test_process_metrics_serialization():
    """Verify the ProcessMetrics contract drops null parameters on serialization."""
    metrics = ProcessMetrics(
        inserted_rows=5000,
        primary_key="order_id"
    )
    serialized = metrics.to_dict()
    
    assert serialized["inserted_rows"] == 5000
    assert serialized["primary_key"] == "order_id"
    # Optional unassigned fields must be dropped to preserve metadata clutter cleanliness
    assert "watermark_column" not in serialized
    assert "updated_rows" in serialized  # Defaults to 0, so it remains present


def test_decorator_intercepts_metrics(monkeypatch):
    """Verify that @log_task automatically captures and logs the ProcessMetrics data contract."""
    # Mock the internal logger stream call to capture the structural output intercept
    mock_logger = MagicMock()
    
    # FIX: Accept positional and keyword arguments (*args, **kwargs) so name parameter doesn't fail
    monkeypatch.setattr("logging.getLogger", lambda *args, **kwargs: mock_logger)
    
    test_metrics = ProcessMetrics(
        inserted_rows=120,
        updated_rows=10,
        watermark_column="created_at",
        watermark_value="2026-07-16"
    )

    @log_task("dimension_load")
    def run_etl():
        return test_metrics

    run_etl()

    # Ensure the wrapper successfully executed info entries
    assert mock_logger.info.call_count == 2
    
    # Intercept the second call ('Task completed' phase)
    last_call_args, last_call_kwargs = mock_logger.info.call_args
    
    assert "operational_metrics" in last_call_kwargs["extra"]
    metrics_payload = last_call_kwargs["extra"]["operational_metrics"]
    assert metrics_payload["inserted_rows"] == 120
    assert metrics_payload["watermark_column"] == "created_at"