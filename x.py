import time
import random
from datetime import datetime

# 1. Import core factory, configuration, and the inline context timer
from data_logger import get_logger, LoggerConfig, timer_scope,log_task_by_ref, ProcessMetrics, log_task

# 2. Configure the engine to permit metadata structural formats
console_config = LoggerConfig(
    include_lineage=True  # 💡 MUST BE TRUE so the engine exposes the metadata schema block
)
logger = get_logger(name="DE_Timing_Pipeline", config=console_config)

# 3. Extract Task 
@log_task("API Extraction Phase")
def extract_data():
    # ⏱️ Enclose inside the properly spelled context manager
    logger.info("Starting extraction from upstream API endpoints...")
    time.sleep(0.5)  # Simulating network latency [cite: 44]
    
    mock_records = [{"id": i, "value": random.randint(10, 100)} for i in range(1, 101)]
    
    logger.info(f"Successfully extracted {len(mock_records)} source records.")
    # log_ctx["row_count"] = len(mock_records)
    # log_ctx["source"] = 'upstream_api'
    return mock_records

# 4. Transform Task 
@log_task("Data Transformation Phase")
def transform_data(raw_data):
    cleaned_data = []
    
    logger.info("Beginning data cleansing and schema validation transforms.")
    for row in raw_data:
        if row["value"] % 2 == 0:
            cleaned_data.append({"user_id": row["id"], "score": row["value"], "status": "ACTIVE"})
        else:
            cleaned_data.append({"user_id": row["id"], "score": row["value"] * 10, "status": "UPDATED"})
    time.sleep(0.3)  # Simulating compute processing time

    logger.info(f"Transformations complete. Processed {len(cleaned_data)} records locally.")
    return cleaned_data

# 5. Main Pipeline Orchestration
def run_pipeline():
        logger.info("=== Initializing ETL Pipeline Execution ===")
        
        try:
            raw_payload = extract_data()
            final_data = transform_data(raw_payload)
            logger.info("=== ETL Pipeline Completed Successfully ===")
            
        except Exception as e:
            logger.error(f"Pipeline crashed due to unhandled exception: {str(e)}")
            raise e
            
        finally:
            logger.info("Pipeline execution finished. Staging cache was bypassed safely.")

if __name__ == "__main__":
    run_pipeline()