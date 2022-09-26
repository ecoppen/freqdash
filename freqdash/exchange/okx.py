import logging
from decimal import Decimal

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
        params = {"instType": "SPOT", "instId": f"{base.upper()}-{quote.upper()}"}

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
