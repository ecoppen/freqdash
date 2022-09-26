import logging
from decimal import Decimal

from freqdash.exchange.exchange import Exchange
from freqdash.exchange.utils import send_public_request

log = logging.getLogger(__name__)


class Gateio(Exchange):
    def __init__(self):
        super().__init__()

    exchange = "gate.io"
    spot_api_url = "https://api.gateio.ws"
    futures_api_url = "https://fx-api.gateio.ws"
    max_weight = 1000

    def get_spot_price(self, base: str, quote: str) -> Decimal:
        self.check_weight()
        params = {"currency_pair": f"{base}_{quote}"}
        header, raw_json = send_public_request(
            api_url=self.spot_api_url, url_path="/api/v4/spot/tickers", payload=params
        )
        if len(raw_json) > 0:
            if "last" in raw_json[0]:
                return Decimal(raw_json[0]["last"])
        return Decimal(-1.0)

    def get_spot_prices(self) -> list[dict[str, Decimal]]:
        self.check_weight()
        params: dict = {}
        header, raw_json = send_public_request(
            api_url=self.spot_api_url, url_path="/api/v4/spot/tickers", payload=params
        )
        return [
            {"symbol": pair["currency_pair"], "price": Decimal(pair["last"])}
            for pair in raw_json
        ]
