import logging
from decimal import Decimal
from typing import Union

from freqdash.exchange.exchange import Exchange
from freqdash.exchange.utils import Intervals, send_public_request

log = logging.getLogger(__name__)


class Binance(Exchange):
    def __init__(self):
        super().__init__()
        log.info("Binance initialised")

    exchange = "binance"
    spot_api_url = "https://api.binance.com"
    futures_api_url = "https://fapi.binance.com"
    max_weight = 1000

    def get_spot_price(
        self, base: Union[str, None] = None, quote: Union[str, None] = None
    ) -> Decimal:
        self.check_weight()
        params = {}
        if base is not None and quote is not None:
            params["symbol"] = f"{base}{quote}"
        else:
            return Decimal(-1.0)
        header, raw_json = send_public_request(
            api_url=self.spot_api_url, url_path="/api/v3/ticker/price", payload=params
        )
        self.update_weight(int(header["X-MBX-USED-WEIGHT-1M"]))
        return Decimal(raw_json["price"])

    def get_spot_prices(self) -> list[dict[str, Decimal]]:
        self.check_weight()
        params: dict = {}
        header, raw_json = send_public_request(
            api_url=self.spot_api_url, url_path="/api/v3/ticker/price", payload=params
        )
        self.update_weight(int(header["X-MBX-USED-WEIGHT-1M"]))
        return [
            {"symbol": pair["symbol"], "price": Decimal(pair["price"])}
            for pair in raw_json
        ]

    def get_spot_kline(
        self,
        symbol: str,
        interval: Intervals,
        start_time: Union[int, None] = None,
        end_time: Union[int, None] = None,
        limit: int = 500,
    ) -> dict:
        self.check_weight()
        params = {"symbol": symbol, "interval": interval, "limit": limit}
        if start_time is not None:
            params["startTime"] = start_time
        if end_time is not None:
            params["endTime"] = end_time

        header, raw_json = send_public_request(
            api_url=self.spot_api_url, url_path="/api/v3/klines", payload=params
        )
        self.update_weight(int(header["X-MBX-USED-WEIGHT-1M"]))
        return raw_json
