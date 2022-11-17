import logging
from decimal import Decimal
from typing import Union

from freqdash.exchange.exchange import Exchange
from freqdash.exchange.utils import Intervals, Settle, send_public_request

log = logging.getLogger(__name__)


class Binance(Exchange):
    def __init__(self):
        super().__init__()
        log.info("Binance initialised")

    exchange = "binance"
    spot_api_url = "https://api.binance.com"
    spot_trade_url = "https://www.binance.com/en/trade/BASE_QUOTE"
    futures_api_url = "https://fapi.binance.com"
    futures_trade_url = "https://www.binance.com/en/futures/BASEQUOTE"
    max_weight = 1000

    def get_spot_price(self, base: str, quote: str) -> Decimal:
        self.check_weight()
        params: dict = {"symbol": f"{base}{quote}"}
        header, raw_json = send_public_request(
            api_url=self.spot_api_url, url_path="/api/v3/ticker/price", payload=params
        )
        self.update_weight(int(header["X-MBX-USED-WEIGHT-1M"]))
        if "price" in [*raw_json]:
            return Decimal(raw_json["price"])
        return Decimal(-1.0)

    def get_spot_prices(self) -> list[dict[str, Decimal]]:
        self.check_weight()
        params: dict = {}
        header, raw_json = send_public_request(
            api_url=self.spot_api_url, url_path="/api/v3/ticker/price", payload=params
        )
        self.update_weight(int(header["X-MBX-USED-WEIGHT-1M"]))
        if len(raw_json) > 0:
            return [
                {"symbol": pair["symbol"], "price": Decimal(pair["price"])}
                for pair in raw_json
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
        params: dict = {
            "symbol": f"{base}{quote}",
            "interval": interval,
            "limit": limit,
        }
        if start_time is not None:
            params["startTime"] = start_time
        if end_time is not None:
            params["endTime"] = end_time

        header, raw_json = send_public_request(
            api_url=self.spot_api_url, url_path="/api/v3/klines", payload=params
        )
        self.update_weight(int(header["X-MBX-USED-WEIGHT-1M"]))
        if len(raw_json) > 0:
            return [
                {
                    "timestamp": int(candle[0]),
                    "open": Decimal(candle[1]),
                    "high": Decimal(candle[2]),
                    "low": Decimal(candle[3]),
                    "close": Decimal(candle[4]),
                    "volume": Decimal(candle[5]),
                }
                for candle in raw_json
            ]
        return []

    def get_futures_price(self, base: str, quote: str) -> Decimal:
        self.check_weight()
        params: dict = {"symbol": f"{base}{quote}"}
        header, raw_json = send_public_request(
            api_url=self.futures_api_url,
            url_path="/fapi/v1/ticker/price",
            payload=params,
        )
        self.update_weight(int(header["X-MBX-USED-WEIGHT-1M"]))
        if "price" in [*raw_json]:
            return Decimal(raw_json["price"])
        return Decimal(-1.0)

    def get_futures_prices(self) -> list:
        self.check_weight()
        params: dict = {}
        header, raw_json = send_public_request(
            api_url=self.futures_api_url,
            url_path="/fapi/v1/ticker/price",
            payload=params,
        )
        self.update_weight(int(header["X-MBX-USED-WEIGHT-1M"]))
        if len(raw_json) > 0:
            return [
                {"symbol": pair["symbol"], "price": Decimal(pair["price"])}
                for pair in raw_json
            ]
        return []

    def get_futures_kline(
        self,
        base: str,
        quote: str,
        start_time: Union[int, None] = None,
        end_time: Union[int, None] = None,
        interval: Intervals = Intervals.ONE_DAY,
        limit: int = 500,
        settle: Union[Settle, None] = None,
    ) -> list:
        self.check_weight()
        params: dict = {
            "symbol": f"{base}{quote}",
            "interval": interval,
            "limit": limit,
        }
        if start_time is not None:
            params["startTime"] = start_time
        if end_time is not None:
            params["endTime"] = end_time

        header, raw_json = send_public_request(
            api_url=self.futures_api_url, url_path="/fapi/v1/klines", payload=params
        )
        self.update_weight(int(header["X-MBX-USED-WEIGHT-1M"]))
        if len(raw_json) > 0:
            return [
                {
                    "timestamp": int(candle[0]),
                    "open": Decimal(candle[1]),
                    "high": Decimal(candle[2]),
                    "low": Decimal(candle[3]),
                    "close": Decimal(candle[4]),
                    "volume": Decimal(candle[5]),
                }
                for candle in raw_json
            ]
        return []
