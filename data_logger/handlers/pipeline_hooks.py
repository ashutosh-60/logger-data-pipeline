import os
from typing import Optional, Any

def flush_logs(db_csv_path: str = "db_cache.csv", 
               delta_csv_path: str = "delta_cache.csv", 
               sql_engine: Optional[Any] = None, 
               table_name: str = "pipeline_logs",
               delta_table_path: Optional[str] = None) -> None:
    """
    Unified post-execution hook to execute high-performance bulk processing.
    Supports PostgreSQL, MySQL, and SQL Server out-of-the-box via SQLAlchemy engines.
    """
    import pandas as pd
    
    # 1. Bulk Lifter for SQL Databases (PGSQL, MySQL, SQL Server)
    if sql_engine and os.path.exists(db_csv_path):
        try:
            # Load the localized staging logs
            df_sql = pd.read_csv(db_csv_path)
            
            if not df_sql.empty:
                # Perform high-speed bulk insert into the user's specific database table
                # chunksize handles memory management for massive log volumes
                df_sql.to_sql(
                    name=table_name, 
                    con=sql_engine, 
                    if_exists="append", 
                    index=False,
                    chunksize=1000
                )
                
                # Safeguard: Clean up the localized cache only after successful DB commit
                os.remove(db_csv_path)
                
        except Exception as e:
            # Fail gracefully to console so the main data transformation isn't corrupted
            print(f"[DataLogger Error] Failed bulk upload to database table '{table_name}': {e}")

    # 2. Bulk Lifter for Delta Lake
    if delta_table_path and os.path.exists(delta_csv_path):
        try:
            df_delta = pd.read_csv(delta_csv_path)
            if not df_delta.empty:
                # High-throughput append directly into Delta lake storage
                # Preserves storage optimization by writing a singular aggregated payload
                df_delta.to_parquet(delta_table_path, mode="append")
                os.remove(delta_csv_path)
        except Exception as e:
            print(f"[DataLogger Error] Failed bulk upload to Delta path '{delta_table_path}': {e}")