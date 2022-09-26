import logging
from decimal import Decimal
from typing import Union

from freqdash.exchange.exchange import Exchange
from freqdash.exchange.utils import Intervals, send_public_request

log = logging.getLogger(__name__)


class Okx(Exchange):
    def __init__(self):
        super().__init__()
        log.info("Okx initialised")

    exchange = "okx"
    spot_api_url = "https://www.okx.com"
    futures_api_url = "https://www.okx.com"
    max_weight = 600

    def get_spot_price(self, base: str, quote: str) -> Decimal:
        self.check_weight()
        params = {"instType": "SPOT", "instId": f"{base}-{quote}"}

        header, raw_json = send_public_request(
            api_url=self.spot_api_url, url_path="/api/v5/market/ticker", payload=params
        )
        if "data" in [*raw_json]:
            if len(raw_json["data"]) > 0:
                if "last" in [*raw_json["data"][0]]:
                    return Decimal(raw_json["data"][0]["last"])
        return Decimal(-1.0)

    def get_spot_prices(self) -> list:
        self.check_weight()
        params = {"instType": "SPOT"}
        header, raw_json = send_public_request(
            api_url=self.spot_api_url, url_path="/api/v5/market/tickers", payload=params
        )
        if "data" in [*raw_json]:
            if len(raw_json["data"]) > 0:
                return [
                    {
                        "symbol": pair["instId"].replace("-", ""),
                        "price": Decimal(pair["last"]),
                    }
                    for pair in raw_json["data"]
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
        custom_intervals = {
            "1m": "1m",
            "5m": "5m",
            "15m": "15m",
            "1h": "1H",
            "4h": "4H",
            "1d": "1D",
            "1w": "1W",
        }
        params: dict = {
            "instId": f"{base}-{quote}",
            "bar": custom_intervals[interval],
            "limit": limit,
        }
        if start_time is not None:
            params["after"] = start_time
        if end_time is not None:
            params["before"] = end_time

        header, raw_json = send_public_request(
            api_url=self.spot_api_url, url_path="/api/v5/market/candles", payload=params
        )

        if "data" in [*raw_json]:
            if len(raw_json["data"]) > 0:
                return [
                    {
                        "timestamp": int(candle[0]),
                        "open": Decimal(candle[1]),
                        "high": Decimal(candle[2]),
                        "low": Decimal(candle[3]),
                        "close": Decimal(candle[4]),
                        "volume": Decimal(candle[5]),
                    }
                    for candle in raw_json["data"]
                ]
        return []
