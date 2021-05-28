from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Union

from dataclasses_json.api import dataclass_json
from dataclasses_json.cfg import config
from stringcase import camelcase


def datetime_encoder(dt: Optional[datetime] = None) -> Optional[str]:
    if dt is None:
        return None

    return dt.isoformat()


@dataclass_json(letter_case=camelcase)
@dataclass
class Browser:
    name: str
    version: str
    comment: Optional[str] = None


@dataclass_json(letter_case=camelcase)
@dataclass
class Creator:
    name: str
    version: str
    comment: Optional[str] = None


@dataclass_json(letter_case=camelcase)
@dataclass
class CacheState:
    last_access: str
    e_tag: str
    hit_count: int
    expires: Optional[str] = None


@dataclass_json(letter_case=camelcase)
@dataclass
class Cache:
    before_request: Optional[CacheState] = None
    after_request: Optional[CacheState] = None
    comment: Optional[str] = None


@dataclass_json(letter_case=camelcase)
@dataclass
class QueryParameter:
    name: str
    value: str


@dataclass_json(letter_case=camelcase)
@dataclass
class Header:
    name: str
    value: str


@dataclass_json(letter_case=camelcase)
@dataclass
class Cookie:
    name: str
    value: str
    path: Optional[str] = None
    domain: Optional[str] = None
    expires: Optional[datetime] = field(
        default=None,
        metadata=config(
            encoder=datetime_encoder,
        ),
    )
    http_only: Optional[bool] = None
    secure: Optional[bool] = None
    same_site: Optional[str] = None


@dataclass_json(letter_case=camelcase)
@dataclass
class Param:
    name: str
    value: Optional[str] = None
    file_name: Optional[str] = None
    content_type: Optional[str] = None


@dataclass_json(letter_case=camelcase)
@dataclass
class PostData:
    mime_type: str
    params: List[Param]
    text: str


@dataclass_json(letter_case=camelcase)
@dataclass
class Request:
    method: str
    url: str
    http_version: str
    cookies: List[Cookie]
    headers: List[Header]
    query_string: List[QueryParameter]
    headers_size: int
    body_size: int
    post_data: Optional[PostData] = None
    comment: Optional[str] = None


@dataclass_json(letter_case=camelcase)
@dataclass
class Content:
    size: int
    compression: Optional[int] = None
    mime_type: Optional[str] = None
    text: Optional[str] = None
    encoding: Optional[str] = None
    comment: Optional[str] = None


@dataclass_json(letter_case=camelcase)
@dataclass
class Response:
    status: int
    status_text: str
    http_version: str
    cookies: List[Cookie]
    headers: List[Header]
    content: Content
    headers_size: int
    body_size: int
    redirect_url: str = field(metadata=config(field_name="redirectURL"))
    comment: Optional[str] = None
    _remote_ip_address: Optional[str] = field(
        default=None, metadata=config(field_name="_remoteIPAddress")
    )


@dataclass_json(letter_case=camelcase)
@dataclass
class Timings:
    send: Union[int, float]
    wait: Union[int, float]
    receive: Union[int, float]
    blocked: Optional[Union[int, float]] = None
    dns: Optional[Union[int, float]] = None
    connect: Optional[Union[int, float]] = None
    ssl: Optional[Union[int, float]] = None
    comment: Optional[Union[int, float]] = None


@dataclass_json(letter_case=camelcase)
@dataclass
class Entry:
    started_date_time: datetime = field(
        metadata=config(
            encoder=datetime_encoder,
        )
    )
    time: Union[int, float]
    request: Request
    response: Response
    cache: Cache
    timings: Timings
    pageref: Optional[str] = None
    server_ip_address: Optional[str] = field(
        default=None, metadata=config(field_name="serverIPAddress")
    )
    comment: Optional[str] = None


@dataclass_json(letter_case=camelcase)
@dataclass
class PageTimings:
    on_content_load: Union[int, float, None] = None
    on_load: Union[int, float, None] = None
    comment: Optional[str] = None


@dataclass_json(letter_case=camelcase)
@dataclass
class Page:
    started_date_time: datetime = field(metadata=config(encoder=datetime_encoder))
    id: str
    title: str
    page_timings: PageTimings
    comment: Optional[str] = None


@dataclass_json(letter_case=camelcase)
@dataclass
class Log:
    version: str
    creator: Creator
    browser: Browser
    pages: List[Page]
    entries: List[Entry]
    comment: Optional[str] = None


@dataclass_json(letter_case=camelcase)
@dataclass
class Har:
    log: Log
