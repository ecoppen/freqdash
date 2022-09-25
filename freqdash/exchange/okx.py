import logging

from freqdash.exchange.exchange import Exchange
from freqdash.exchange.utils import send_public_request

log = logging.getLogger(__name__)


class Okx(Exchange):
    def __init__(self):
        super().__init__()

    exchange = "okx"
    spot_api_url = "https://www.okx.com"
    futures_api_url = "https://www.okx.com"
    max_weight = 600

    def get_spot_prices(self):
        params = {"instType": "SPOT"}
        header, raw_json = send_public_request(
            self.spot_api_url, "/api/v5/market/tickers", params
        )
        return [
            {"symbol": sym["instId"].replace("-", ""), "price": sym["last"]}
            for sym in raw_json["data"]
        ]
