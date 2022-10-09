import hashlib
import hmac
import logging
import time
from enum import Enum
from urllib.parse import urlencode

import requests  # type: ignore

log = logging.getLogger(__name__)


def hashing(query_string, secret):
    return hmac.new(
        secret.encode("utf-8"),
        query_string.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def get_timestamp():
    return int(time.time() * 1000)


class HTTPRequestError(Exception):
    def __init__(self, url, code, msg=None):
        self.url = url
        self.code = code
        self.msg = msg

    def __str__(self) -> str:
        return f"Request to {self.url!r} failed. Code: {self.code}; Message: {self.msg}"


def dispatch_request(http_method, key=None):
    session = requests.Session()
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


def send_public_request(api_url: str, url_path: str, payload=None):
    if payload is None:
        payload = {}
    query_string = urlencode(payload, True)
    url = api_url + url_path
    if query_string:
        url = url + "?" + query_string
    log.info(f"Requesting: {url}")
    response = dispatch_request("GET")(url=url)
    headers = response.headers
    json_response = response.json()
    if "code" in json_response and "msg" in json_response:
        if len(json_response["msg"]) > 0:
            raise HTTPRequestError(
                url=url, code=json_response["code"], msg=json_response["msg"]
            )
    return headers, json_response


class Exchanges(str, Enum):
    BINANCE = "binance"
    BYBIT = "bybit"
    GATEIO = "gateio"
    KUCOIN = "kucoin"
    OKX = "okx"


class Markets(str, Enum):
    FUTURES = "FUTURES"
    SPOT = "SPOT"


class Intervals(str, Enum):
    ONE_MINUTE = "1m"
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    ONE_HOUR = "1h"
    FOUR_HOURS = "4h"
    ONE_DAY = "1d"
    ONE_WEEK = "1w"


class Settle(str, Enum):
    BTC = "btc"
    USD = "usd"
    USDT = "usdt"
