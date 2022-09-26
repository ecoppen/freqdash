import logging
from decimal import Decimal

from freqdash.exchange.exchange import Exchange
from freqdash.exchange.utils import Intervals, send_public_request

log = logging.getLogger(__name__)


class Kucoin(Exchange):
    def __init__(self):
        super().__init__()
        log.info("Kucoin initialised")

    exchange = "kucoin"
    spot_api_url = "https://api.kucoin.com"
    futures_api_url = "https://api-futures.kucoin.com"
    max_weight = 600

    def get_spot_price(self, base: str, quote: str) -> Decimal:
        self.check_weight()
        params = {"symbol": f"{base}-{quote}"}
        header, raw_json = send_public_request(
            api_url=self.spot_api_url,
            url_path="/api/v1/market/orderbook/level1",
            payload=params,
        )
        if "data" in [*raw_json]:
            if "price" in [*raw_json["data"]]:
                return Decimal(raw_json["data"]["price"])
        return Decimal(-1.0)

    def get_spot_prices(self) -> list:
        self.check_weight()
        params: dict = {}
        header, raw_json = send_public_request(
            api_url=self.spot_api_url,
            url_path="/api/v1/market/allTickers",
            payload=params,
        )
        if "data" in [*raw_json]:
            if "ticker" in [*raw_json["data"]]:
                return [
                    {
                        "symbol": pair["symbol"].replace("-", ""),
                        "price": Decimal(pair["last"]),
                    }
                    for pair in raw_json["data"]["ticker"]
                ]
        return []
