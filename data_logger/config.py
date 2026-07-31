from dataclasses import dataclass
from typing import Optional

@dataclass
class LoggerConfig:
    """
    Configuration model to toggle destinations and inject custom schemas.
    """
    enable_console: bool = True
    include_lineage: bool = True
    time_trackker: bool = True
    
    # Placeholders for future Test
    enable_sql: bool = False
    enable_delta: bool = False
    custom_schema: Optional[str] = None
    sql_connection_string: Optional[str] = None
    delta_file_path: Optional[str] = None