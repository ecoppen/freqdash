import logging

from freqdash.exchange.exchange import Exchange
from freqdash.exchange.utils import send_public_request

log = logging.getLogger(__name__)


class Kucoin(Exchange):
    def __init__(self):
        super().__init__()

    exchange = "kucoin"
    spot_api_url = "https://api.kucoin.com"
    futures_api_url = "https://api-futures.kucoin.com"
    max_weight = 600

    def get_spot_prices(self):
        self.check_weight()
        header, raw_json = send_public_request(
            self.spot_api_url, "/api/v1/market/allTickers"
        )
        # self.update_weight(int(header['X-MBX-USED-WEIGHT-1M']))
        return [
            {"symbol": sym["symbol"].replace("-", ""), "price": sym["last"]}
            for sym in raw_json["data"]["ticker"]
        ]
