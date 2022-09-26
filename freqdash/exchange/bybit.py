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
    futures_api_url = "https://api.bybit.com"
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
        params = {"symbol": {f"{base}{quote}"}, "interval": interval, "limit": limit}
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
