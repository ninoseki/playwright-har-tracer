from datetime import datetime
from typing import Optional


def datetime_encoder(dt: Optional[datetime] = None) -> Optional[str]:
    if dt is None:
        return None

    return dt.isoformat()
