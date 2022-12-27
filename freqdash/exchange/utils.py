import logging
from enum import Enum

import requests  # type: ignore

log = logging.getLogger(__name__)


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
