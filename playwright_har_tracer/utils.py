import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from urllib.parse import parse_qs

import dateutil.parser
from playwright.async_api import Request

from . import dataclasses


def millis_to_roundish_millis(value: float) -> int:
    return int(int(value * 1000) / 1000)


def datetime_to_millis(dt: datetime) -> float:
    return dt.timestamp() * 1000.0


def query_to_query_params(query: str) -> List[dataclasses.har.QueryParameter]:
    query_params: List[dataclasses.har.QueryParameter] = []

    parsed_query_params = parse_qs(query)
    for name, values in parsed_query_params.items():
        value = "".join(values)
        query_params.append(dataclasses.har.QueryParameter(name=name, value=value))

    return query_params


def form_data_to_params(data: str) -> List[dataclasses.har.Param]:
    params = query_to_query_params(data)
    return [
        dataclasses.har.Param(name=param.name, value=param.value) for param in params
    ]


def dict_to_headers(dict_: Dict[str, str]) -> List[dataclasses.har.Header]:
    return [
        dataclasses.har.Header(name=name, value=value) for name, value in dict_.items()
    ]


def parse_cookie(c: str) -> dataclasses.har.Cookie:
    cookie = dataclasses.har.Cookie(name="", value="")

    first = True
    for pair in re.split(r"; *", c):
        pair = str(pair)

        index_of_equals = -1
        if "=" in pair:
            index_of_equals = pair.index("=")

        name = pair[0:index_of_equals] if index_of_equals != -1 else pair.strip()
        value = pair[index_of_equals + 1 :] if index_of_equals != -1 else ""

        if first:
            first = False
            cookie.name = name
            cookie.value = value
            continue

        if name == "Domain":
            cookie.domain = value

        if name == "Expires":
            cookie.expires = dateutil.parser.parse(value)

        if name == "HttpOnly":
            cookie.http_only = True

        if name == "Max-Age":
            max_age = datetime.now() + timedelta(seconds=int(value))
            cookie.expires = max_age

        if name == "Path":
            cookie.path = value

        if name == "SameSite":
            cookie.same_site = value

        if name == "Secure":
            cookie.secure = True

    return cookie


def cookies_for_har(
    header: Optional[str],
    separator: str,
) -> List[dataclasses.har.Cookie]:
    if header is None:
        return []

    return [parse_cookie(c) for c in header.split(separator)]


def post_data_for_har(request: Request) -> Optional[dataclasses.har.PostData]:
    post_data = request.post_data_buffer
    if post_data is None:
        return None

    content_type = request.headers.get("content-type", "application/octet-stream")
    text = "" if content_type == "application/octet-stream" else post_data.decode()
    result = dataclasses.har.PostData(mime_type=content_type, text=text, params=[])

    if content_type == "application/x-www-form-urlencoded":
        form_data = post_data.decode()
        result.params.extend(form_data_to_params(form_data))

    return result


def set_remote_ip_address_as_comment(
    har: dataclasses.har.Har,
    response_received_events: List[dataclasses.cdp.ResponseReceivedEvent],
):
    # url -> remote_ip_address table
    memo: Dict[str, Optional[str]] = {}
    for event in response_received_events:
        key = event.response.url
        value = event.response.remote_ip_address
        memo[key] = value

    # set a remote IP address as a comment
    for entry in har.log.entries:
        url = entry.request.url
        remote_ip_address = memo.get(url)
        entry.response.comment = remote_ip_address
        entry.response._remote_ip_address = remote_ip_address

    return har
