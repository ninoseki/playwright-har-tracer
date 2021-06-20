from datetime import datetime
from typing import Any, Optional

from boltons.iterutils import remap


def datetime_encoder(dt: Optional[datetime] = None) -> Optional[str]:
    if dt is None:
        return None

    return dt.isoformat()


def reject_none_encoder(d: dict) -> dict:
    # According to the HAR v1.2 spec, None (Null) values are not permitted.
    # So remove None values when encoding the log to JSON
    def remove_none(_, key: Any, value: Any):
        return key is not None and value is not None

    cleaned = remap(d, visit=remove_none)
    return cleaned
