import csv
import json
import os
from logging import Handler, LogRecord

class CSVStagingHandler(Handler):
    """
    Custom logging handler that maps JSON log elements into a local CSV cache
    to avoid mid-pipeline network I/O overhead.
    """
    def __init__(self, filepath: str):
        super().__init__()
        self.filepath = filepath
        # Standard schema columns for our data engineering audit trail
        self.headers = [
            "timestamp", "levelname", "name", "filename", 
            "funcName", "lineno", "message", "metadata"
        ]
        
        # Initialize the CSV file with headers if it doesn't exist
        if not os.path.exists(self.filepath):
            with open(self.filepath, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(self.headers)

    def emit(self, record: LogRecord):
        try:
            # Format using our JSON formatter built in Phase 2
            log_json_str = self.format(record)
            log_data = json.loads(log_json_str)
            
            # Separate Core standard fields from custom dynamic metadata
            core_fields = {k: log_data.get(k) for k in self.headers[:-1]}
            
            # Bundle any extra columns provided by the user into the metadata payload
            custom_metadata = {
                k: v for k, v in log_data.items() 
                if k not in core_fields and k != "asctime"
            }
            
            # Map values explicitly matching our headers array
            row = [
                log_data.get("asctime"),
                core_fields["levelname"],
                core_fields["name"],
                core_fields["filename"],
                core_fields["funcName"],
                core_fields["lineno"],
                core_fields["message"],
                json.dumps(custom_metadata) # Core + JSON Design Pattern
            ]
            
            with open(self.filepath, mode='a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(row)
                
        except Exception:
            self.handleError(record) # Fail gracefully to console if local write fails