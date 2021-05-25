from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from dataclasses_json.api import dataclass_json
from dataclasses_json.cfg import config
from stringcase import camelcase


@dataclass_json(letter_case=camelcase)
@dataclass
class Response:
    url: str
    status: int
    status_text: str
    headers: Dict[str, Any]
    mime_type: str
    connection_reused: bool
    connection_id: int
    encoded_data_length: int
    security_state: str
    response_time: Optional[float] = None
    request_headers: Optional[Dict[str, Any]] = None
    request_headers_text: Optional[str] = None
    remote_ip_address: Optional[str] = field(
        default=None, metadata=config(field_name="remoteIPAddress")
    )
    remote_port: Optional[int] = None
    from_disk_cache: Optional[bool] = None
    from_service_worker: Optional[bool] = None
    from_prefetch_cache: Optional[bool] = None
    timing: Optional[Dict[str, float]] = None
    protocol: Optional[str] = None
    headers_text: Optional[str] = None


@dataclass_json(letter_case=camelcase)
@dataclass
class ResponseReceivedEvent:
    request_id: str
    loader_id: str
    timestamp: float
    type: str
    response: Response
    frame_id: str
