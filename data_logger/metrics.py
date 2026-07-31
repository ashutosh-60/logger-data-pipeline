from dataclasses import dataclass, asdict
from typing import Optional, Any

@dataclass(frozen=True)
class ProcessMetrics:
    """
    Standardized operational contract to record high-value pipeline metrics.
    Ensures absolute naming uniformity across log targets.
    """
    inserted_rows: int = 0
    updated_rows: int = 0
    deleted_rows: int = 0
    watermark_column: Optional[str] = None
    watermark_value: Optional[Any] = None
    primary_key: Optional[str] = None

    def to_dict(self) -> dict:
        """Serializes the contract fields for metadata injection."""
        return {k: v for k, v in asdict(self).items() if v is not None}