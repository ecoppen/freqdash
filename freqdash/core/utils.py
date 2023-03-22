import json
import logging
import re
from datetime import datetime, timedelta
from urllib.parse import urlencode

import requests  # type: ignore

log = logging.getLogger(__name__)


class HTTPRequestError(Exception):
    def __init__(self, url, code, msg=None):
        self.url = url
        self.code = code
        self.msg = msg

    def __str__(self) -> str:
        return f"Request to {self.url!r} failed. Code: {self.code}; Message: {self.msg}"


class BlankResponse:
    def __init__(self):
        self.content = ""


def dispatch_request(http_method, key=None, auth=None):
    session = requests.Session()
    session.auth = auth
    session.headers.update(
        {
            "Content-Type": "application/json;charset=utf-8",
            "X-MBX-APIKEY": key,
        }
    )
    return {
        "GET": session.get,
        "DELETE": session.delete,
        "PUT": session.put,
        "POST": session.post,
    }.get(http_method, "GET")


def send_public_request(
    url: str,
    method: str = "GET",
    url_path: str | None = None,
    payload: dict | None = None,
    auth: tuple | None = None,
    access_token: str | None = None,
    json: bool = True,
):
    empty_response = BlankResponse().content
    if url_path is not None:
        url += url_path
    if payload is None:
        payload = {}
    query_string = urlencode(payload, True)
    if query_string:
        url = url + "?" + query_string

    log.debug(f"Requesting {url}")
    headers = {"Authorization": f"Bearer {access_token}"}

    try:
        response = dispatch_request(method)(
            url=url, auth=auth, timeout=5, headers=headers
        )
        headers = response.headers
        if not json:
            return headers, response.text
        json_response = response.json()
        if "code" in json_response and "msg" in json_response:
            if len(json_response["msg"]) > 0:
                raise HTTPRequestError(
                    url=url, code=json_response["code"], msg=json_response["msg"]
                )
        return headers, json_response
    except requests.exceptions.Timeout:
        log.info("Request timed out")
        return empty_response, empty_response
    except requests.exceptions.TooManyRedirects:
        log.info("Too many redirects")
        return empty_response, empty_response
    except requests.exceptions.RequestException as e:
        log.info(f"Request exception: {e}")
        return empty_response, empty_response


def start_datetime_ago(days: int) -> str:
    start_datetime = datetime.combine(
        datetime.now() - timedelta(days=days), datetime.min.time()
    )
    return start_datetime.strftime("%Y-%m-%d %H:%M:%S")


def end_datetime_ago(days: int) -> str:
    start_datetime = datetime.combine(
        datetime.now() - timedelta(days=days), datetime.max.time()
    )
    return start_datetime.strftime("%Y-%m-%d %H:%M:%S")


def start_milliseconds_ago(days: int) -> int:
    start_datetime = datetime.combine(
        datetime.now() - timedelta(days=days), datetime.min.time()
    )
    return int(start_datetime.timestamp() * 1000)


def end_milliseconds_ago(days: int) -> int:
    start_datetime = datetime.combine(
        datetime.now() - timedelta(days=days), datetime.max.time()
    )
    return int(start_datetime.timestamp() * 1000)


def find_in_string(
    string: str,
    start_substring: str,
    end_substring: str | None = None,
    return_json: bool = False,
):
    text = ""
    start_index = string.find(start_substring)
    if start_index > -1:
        if end_substring is None:
            text = string[start_index + len(start_substring) :]
        else:
            end_index = string.find(end_substring, start_index + len(start_substring))
            if end_index > -1:
                text = string[start_index + len(start_substring) : end_index]
        if len(text) > 0 and return_json:
            try:
                text = json.loads(text)
            except ValueError as e:
                log.warning(f"JSON decode error: {e}")
    return text


def find_all_occurrences_in_string(
    string: str, start_substring: str, end_substring: str
) -> list:
    occurences = []
    start_index = string.find(start_substring)
    while start_index > -1:
        end_index = string.find(end_substring, start_index + len(start_substring))
        if end_index == -1:
            break
        text = string[start_index + len(start_substring) : end_index]
        occurences.append(text)
        start_index = string.find(start_substring, start_index + 1)
    return occurences


def remove_non_alphanumeric(string: str) -> str:
    return re.sub("[^0-9a-zA-Z ]+", "", string)


def dt_to_ts(date) -> int:
    return int(date.timestamp() * 1000)
