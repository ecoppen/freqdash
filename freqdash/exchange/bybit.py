import logging

from freqdash.exchange.exchange import Exchange
from freqdash.exchange.utils import send_public_request

log = logging.getLogger(__name__)


class Bybit(Exchange):
    def __init__(self):
        super().__init__()

    exchange = "bybit"
    spot_api_url = "https://api.bybit.com"
    futures_api_url = "https://api.bybit.com"
    max_weight = 120

    def get_spot_prices(self):
        self.check_weight()
        header, raw_json = send_public_request(
            self.spot_api_url, "/spot/quote/v1/ticker/price"
        )
        return raw_json["result"]
