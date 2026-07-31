import logging
from pythonjsonlogger import jsonlogger

def get_json_formatter(custom_schema: str = None, include_lineage: bool = True) -> logging.Formatter:
    """
    Assembles a JSON formatter dynamically by looping through a structural list of schema keys.
    """
    if custom_schema:
        return jsonlogger.JsonFormatter(custom_schema)
        
    # Core structural logging tokens required for standard operations
    schema_elements = [
        '%(asctime)s',
        '%(levelname)s',
        '%(name)s'
    ]
    
    # Dynamically append distributed tracing metrics if the user hasn't opted out
    if include_lineage:
        lineage_elements = [
            '[RunID: %(run_id)s]',
            '[TaskID: %(task_id)s]',
            '[UpstreamID: %(upstream_id)s]'
        ]
        for element in lineage_elements:
            schema_elements.append(element)
            
    # Append the remaining standard data engineering runtime attributes
    runtime_elements = ['%(filename)s', '%(funcName)s', '%(lineno)d', '%(message)s']

    for element in runtime_elements:
        schema_elements.append(element)
        
    # Construct the final format layout string cleanly by joining the built list
    fmt = " ".join(schema_elements)
    
    return jsonlogger.JsonFormatter(fmt)