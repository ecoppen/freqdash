import logging
from decimal import Decimal
from typing import Union

from freqdash.exchange.exchange import Exchange
from freqdash.exchange.utils import Intervals, Settle, send_public_request

log = logging.getLogger(__name__)


class Gateio(Exchange):
    def __init__(self):
        super().__init__()
        log.info("Gate.io initialised")

    exchange = "gate.io"
    spot_api_url = "https://api.gateio.ws"
    spot_trade_url = "https://www.gate.io/trade/BASE_QUOTE"
    futures_api_url = "https://api.gateio.ws"
    futures_trade_url = "https://www.gate.io/futures_trade/USDT/BASE_QUOTE"
    max_weight = 1000

    def get_spot_price(self, base: str, quote: str) -> Decimal:
        self.check_weight()
        params = {"currency_pair": f"{base}_{quote}"}
        header, raw_json = send_public_request(
            api_url=self.spot_api_url, url_path="/api/v4/spot/tickers", payload=params
        )
        if len(raw_json) > 0:
            if "last" in [*raw_json[0]]:
                return Decimal(raw_json[0]["last"])
        return Decimal(-1.0)

    def get_spot_prices(self) -> list[dict[str, Decimal]]:
        self.check_weight()
        params: dict = {}
        header, raw_json = send_public_request(
            api_url=self.spot_api_url, url_path="/api/v4/spot/tickers", payload=params
        )
        if len(raw_json) > 0:
            return [
                {"symbol": pair["currency_pair"], "price": Decimal(pair["last"])}
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
        params = {
            "currency_pair": f"{base}_{quote}",
            "interval": interval,
            "limit": limit,
        }
        if start_time is not None:
            params["from"] = start_time
        if end_time is not None:
            params["to"] = end_time

        header, raw_json = send_public_request(
            api_url=self.spot_api_url,
            url_path="/api/v4/spot/candlesticks",
            payload=params,
        )
        if len(raw_json) > 0:
            return [
                {
                    "timestamp": int(candle[0]),
                    "open": Decimal(candle[5]),
                    "high": Decimal(candle[3]),
                    "low": Decimal(candle[4]),
                    "close": Decimal(candle[2]),
                    "volume": Decimal(candle[1]),
                }
                for candle in raw_json
            ]
        return []

    def get_futures_price(
        self,
        base: str,
        quote: str,
        settle: Settle = Settle.USDT,
    ) -> Decimal:
        self.check_weight()
        params: dict = {}
        header, raw_json = send_public_request(
            api_url=self.spot_api_url,
            url_path=f"/api/v4/futures/{settle}/contracts/{base}_{quote}",
            payload=params,
        )
        if len(raw_json) > 0:
            if "last_price" in [*raw_json]:
                return Decimal(raw_json["last_price"])
        return Decimal(-1.0)

    def get_futures_prices(
        self,
        settle: Settle = Settle.USDT,
    ) -> list[dict[str, Decimal]]:
        self.check_weight()
        params: dict = {}
        header, raw_json = send_public_request(
            api_url=self.spot_api_url,
            url_path=f"/api/v4/futures/{settle}/contracts",
            payload=params,
        )
        if len(raw_json) > 0:
            return [
                {"symbol": pair["name"], "price": Decimal(pair["last_price"])}
                for pair in raw_json
            ]
        return []

    def get_futures_kline(
        self,
        base: str,
        quote: str,
        interval: Intervals = Intervals.ONE_DAY,
        start_time: Union[int, None] = None,
        end_time: Union[int, None] = None,
        limit: int = 500,
        settle: Settle = Settle.USDT,
    ) -> list:
        self.check_weight()
        params: dict = {
            "contract": f"{base}_{quote}",
            "interval": interval,
        }
        if start_time is not None:
            params["from"] = start_time
        if end_time is not None:
            params["to"] = end_time

        header, raw_json = send_public_request(
            api_url=self.spot_api_url,
            url_path=f"/api/v4/futures/{settle}/candlesticks",
            payload=params,
        )

        if len(raw_json) > 0:
            return [
                {
                    "timestamp": int(candle["t"]),
                    "open": Decimal(candle["o"]),
                    "high": Decimal(candle["h"]),
                    "low": Decimal(candle["l"]),
                    "close": Decimal(candle["c"]),
                    "volume": Decimal(candle["v"]),
                }
                for candle in raw_json
            ][:limit]
        return []
