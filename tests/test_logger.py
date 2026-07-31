import json
import logging
import pytest
from data_logger.config import LoggerConfig
from data_logger.formatters import get_json_formatter
from data_logger.logger import get_logger

def test_logger_config_defaults():
    """Verify that LoggerConfig initializes with the correct default states."""
    config = LoggerConfig()
    assert config.enable_console is True
    assert config.enable_sql is False
    assert config.enable_delta is False
    assert config.custom_schema is None


def test_standard_schema_formatter(capsys):
    """Verify that the JSON formatter outputs the expected Data Engineering schema keys."""
    formatter = get_json_formatter()
    
    # Create a dummy LogRecord to test formatting output
    logger = logging.getLogger("test_schema_logger")
    record = logger.makeRecord(
        name=logger.name,
        level=logging.INFO,
        fn="etl_job.py",
        lno=42,
        msg="Testing pipeline schema",
        args=(),
        exc_info=None,
        func="extract_data"
    )
    
    formatted_json = formatter.format(record)
    log_data = json.loads(formatted_json)
    
    # Assert that all standard data engineering keys are present
    assert "asctime" in log_data
    assert log_data["levelname"] == "INFO"
    assert log_data["name"] == "test_schema_logger"
    assert log_data["filename"] == "etl_job.py"
    assert log_data["funcName"] == "extract_data"
    assert log_data["lineno"] == 42
    assert log_data["message"] == "Testing pipeline schema"


def test_custom_schema_override():
    """Verify that a user can completely overwrite the layout with a custom formatting string."""
    custom_fmt = "%(levelname)s %(message)s"
    formatter = get_json_formatter(custom_schema=custom_fmt)
    
    logger = logging.getLogger("test_custom_logger")
    record = logger.makeRecord(
        name=logger.name,
        level=logging.WARNING,
        fn="script.py",
        lno=10,
        msg="Custom schema payload",
        args=(),
        exc_info=None
    )
    
    log_data = json.loads(formatter.format(record))
    
    # Check that ONLY requested parameters exist, omitting filename/lineno
    assert log_data["levelname"] == "WARNING"
    assert log_data["message"] == "Custom schema payload"
    assert "filename" not in log_data
    assert "lineno" not in log_data


def test_factory_attaches_correct_handlers():
    """Verify that the factory wrapper attaches only the explicitly requested handlers."""
    # Scenario A: Default setup (Only Console enabled)
    default_logger = get_logger("default_pipeline")
    assert len(default_logger.handlers) == 1
    assert isinstance(default_logger.handlers[0], logging.StreamHandler)
    
    # Scenario B: Disable everything via explicit configuration
    silent_config = LoggerConfig(enable_console=False, enable_sql=False, enable_delta=False)
    silent_logger = get_logger("silent_pipeline", config=silent_config)
    assert len(silent_logger.handlers) == 0


def test_handler_idempotency():
    """Ensure that calling get_logger multiple times clears old handlers to avoid duplicate logs."""
    config = LoggerConfig(enable_console=True)
    
    # Call factory repeatedly for the same logging namespace
    logger = get_logger("idempotent_pipeline", config=config)
    logger = get_logger("idempotent_pipeline", config=config)
    logger = get_logger("idempotent_pipeline", config=config)
    
    # Handlers should clear and reset, leaving exactly 1 instead of accumulating 3
    assert len(logger.handlers) == 1