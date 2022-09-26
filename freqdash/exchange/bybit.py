import logging
from decimal import Decimal
from typing import Union

from freqdash.exchange.exchange import Exchange
from freqdash.exchange.utils import send_public_request

log = logging.getLogger(__name__)


class Bybit(Exchange):
    def __init__(self):
        super().__init__()
        log.info("Bybit initialised")

    exchange = "bybit"
    spot_api_url = "https://api.bybit.com"
    futures_api_url = "https://api.bybit.com"
    max_weight = 120

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
            api_url=self.spot_api_url,
            url_path="/spot/v3/public/quote/ticker/price",
            payload=params,
        )
        if "result" in raw_json:
            if "price" in raw_json["result"]:
                return Decimal(raw_json["result"]["price"])
        return Decimal(-1.0)

    def get_spot_prices(self) -> list:
        self.check_weight()
        params: dict = {}
        header, raw_json = send_public_request(
            api_url=self.spot_api_url,
            url_path="/spot/v3/public/quote/ticker/price",
            payload=params,
        )
        if "result" in [*raw_json]:
            if "list" in [*raw_json["result"]]:
                return [
                    {"symbol": pair["symbol"], "price": Decimal(pair["price"])}
                    for pair in raw_json["result"]["list"]
                ]
        return []
