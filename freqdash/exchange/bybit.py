import logging
from decimal import Decimal
from typing import Union

from freqdash.exchange.exchange import Exchange
from freqdash.exchange.utils import Intervals, send_public_request

log = logging.getLogger(__name__)


class Bybit(Exchange):
    def __init__(self):
        super().__init__()
        log.info("Bybit initialised")

    exchange = "bybit"
    spot_api_url = "https://api.bybit.com"
    spot_trade_url = "https://www.bybit.com/en-US/trade/spot/BASE/QUOTE"
    futures_api_url = "https://api.bybit.com"
    futures_trade_url = "https://www.bybit.com/trade/usdt/BASEQUOTE"
    max_weight = 120

    def get_spot_price(self, base: str, quote: str) -> Decimal:
        self.check_weight()
        params = {"symbol": f"{base}{quote}"}
        header, raw_json = send_public_request(
            api_url=self.spot_api_url,
            url_path="/spot/v3/public/quote/ticker/price",
            payload=params,
        )
        if "result" in [*raw_json]:
            if "price" in [*raw_json["result"]]:
                return Decimal(raw_json["result"]["price"])
        return Decimal(-1.0)

    def get_spot_prices(self) -> list:
        self.check_weight()
        params: dict = {}
        header, raw_json = send_public_request(
            api_url=self.spot_api_url,
            url_path="/spot/v3/public/quote/ticker/price",
            payload=params,
        )
        if "result" in [*raw_json]:
            if "list" in [*raw_json["result"]]:
                return [
                    {"symbol": pair["symbol"], "price": Decimal(pair["price"])}
                    for pair in raw_json["result"]["list"]
                ]
        return []

    def get_spot_kline(
        self,
        base: str,
        quote: str,
        interval: Intervals = Intervals.ONE_DAY,
        start_time: Union[int, None] = None,
        end_time: Union[int, None] = None,
        limit: int = 500,
    ) -> list:
        self.check_weight()
        params = {"symbol": f"{base}{quote}", "interval": interval, "limit": limit}
        if start_time is not None:
            params["startTime"] = start_time
        if end_time is not None:
            params["endTime"] = end_time

        header, raw_json = send_public_request(
            api_url=self.spot_api_url,
            url_path="/spot/v3/public/quote/kline",
            payload=params,
        )
        if "result" in [*raw_json]:
            if "list" in [*raw_json["result"]]:
                if len(raw_json["result"]["list"]) > 0:
                    return [
                        {
                            "timestamp": int(candle["t"]),
                            "open": Decimal(candle["o"]),
                            "high": Decimal(candle["h"]),
                            "low": Decimal(candle["l"]),
                            "close": Decimal(candle["c"]),
                            "volume": Decimal(candle["v"]),
                        }
                        for candle in raw_json["result"]["list"]
                    ]
        return []

    def get_futures_price(self, base: str, quote: str) -> Decimal:
        self.check_weight()
        params = {"symbol": f"{base}{quote}"}
        header, raw_json = send_public_request(
            api_url=self.futures_api_url,
            url_path="/v2/public/tickers",
            payload=params,
        )
        if "result" in [*raw_json]:
            if len(raw_json["result"]) > 0:
                if "last_price" in [*raw_json["result"][0]]:
                    return Decimal(raw_json["result"][0]["last_price"])
        return Decimal(-1.0)

    def get_futures_prices(self) -> list:
        self.check_weight()
        params: dict = {}
        header, raw_json = send_public_request(
            api_url=self.futures_api_url,
            url_path="/v2/public/tickers",
            payload=params,
        )
        if "result" in [*raw_json]:
            return [
                {"symbol": pair["symbol"], "price": Decimal(pair["last_price"])}
                for pair in raw_json["result"]
            ]
        return []

    def get_futures_kline(
        self,
        base: str,
        quote: str,
        start_time: int,
        interval: Intervals = Intervals.ONE_DAY,
        end_time: Union[int, None] = None,
        limit: int = 500,
    ) -> list:
        self.check_weight()
        custom_intervals = {
            "1m": 1,
            "5m": 5,
            "15m": 15,
            "1h": 60,
            "4h": 240,
            "1d": "D",
            "1w": "W",
        }
        params = {
            "symbol": f"{base}{quote}",
            "interval": custom_intervals[interval],
            "limit": limit,
            "from": start_time,
        }

        if end_time is not None:
            params["endTime"] = end_time

        header, raw_json = send_public_request(
            api_url=self.futures_api_url,
            url_path="/public/linear/kline",
            payload=params,
        )

        if "result" in [*raw_json]:
            if len(raw_json["result"]) > 0:
                return [
                    {
                        "timestamp": int(candle["open_time"]),
                        "open": Decimal(candle["open"]),
                        "high": Decimal(candle["high"]),
                        "low": Decimal(candle["low"]),
                        "close": Decimal(candle["close"]),
                        "volume": Decimal(candle["volume"]),
                    }
                    for candle in raw_json["result"]
                ]
        return []
