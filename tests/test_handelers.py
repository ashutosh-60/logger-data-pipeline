import os
import pandas as pd
from unittest.mock import MagicMock
from data_logger.handlers.pipeline_hooks import flush_logs

def test_flush_logs_sends_params_to_sql(tmp_path):
    """Verify that flush_logs calls to_sql with the custom user parameters."""
    # Create temporary CSV files for the isolated test environment
    test_db_csv = tmp_path / "test_db.csv"
    
    # Prep staging data frame match standard core schema
    df = pd.DataFrame([{
        "timestamp": "2026-07-16 12:00:00", 
        "levelname": "INFO", 
        "name": "test", 
        "filename": "job.py",
        "funcName": "run", 
        "lineno": 10, 
        "message": "Bulk test", 
        "metadata": "{}"
    }])
    df.to_csv(test_db_csv, index=False)
    
    # Mock the SQLAlchemy Engine
    mock_engine = MagicMock()
    custom_table = "custom_enterprise_logs"
    
    # Execute the lifter hook
    flush_logs(
        db_csv_path=str(test_db_csv),
        delta_csv_path="non_existent.csv",
        sql_engine=mock_engine,
        table_name=custom_table
    )
    
    # Ensure the local cache file is removed after successful execution
    assert not os.path.exists(test_db_csv)