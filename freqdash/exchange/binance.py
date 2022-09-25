import logging

from freqdash.exchange.exchange import Exchange
from freqdash.exchange.utils import send_public_request

log = logging.getLogger(__name__)


class Binance(Exchange):
    def __init__(self):
        super().__init__()

    exchange = "binance"
    spot_api_url = "https://api.binance.com"
    futures_api_url = "https://fapi.binance.com"
    max_weight = 1000

    def get_spot_prices(self):
        self.check_weight()
        header, raw_json = send_public_request(
            self.spot_api_url, "/api/v3/ticker/price"
        )
        self.update_weight(int(header["X-MBX-USED-WEIGHT-1M"]))
        return raw_json

    def get_spot_kline(
        self, symbol, interval="1d", start_time=None, end_time=None, limit=500
    ):
        self.check_weight()
        params = {"symbol": symbol, "interval": interval, "limit": limit}
        if start_time is not None:
            params["startTime"] = start_time
        if end_time is not None:
            params["endTime"] = end_time

        header, raw_json = send_public_request(
            self.spot_api_url, "/api/v3/klines", payload=params
        )
        self.update_weight(int(header["X-MBX-USED-WEIGHT-1M"]))
        return float(raw_json[0][4])
