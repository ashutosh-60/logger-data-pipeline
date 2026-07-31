import json
import logging

import time
import random

from data_logger.config import LoggerConfig
from data_logger.formatters import get_json_formatter
from data_logger import get_logger, timer_scope,log_task

console_config = LoggerConfig(
    include_lineage=True
)
logger = get_logger(name="DE_Timing_Pipeline", config=console_config)
@log_task("API Extraction Phase")
def extract_data():

    # with timer_scope("API Extraction Phase"):
    logger.info("Starting extraction from upstream API endpoints...")
    time.sleep(0.5)  
    mock_records = [{"id": i, "value": random.randint(10, 100)} for i in range(1, 101)]
    logger.info(f"Successfully extracted {len(mock_records)} source records.")

    return mock_records

if __name__ == "__main__":
    extract_data()