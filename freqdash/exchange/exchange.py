import logging
import time
from decimal import Decimal
from typing import Union

from freqdash.exchange.utils import Intervals

log = logging.getLogger(__name__)


class Exchange:
    def __init__(self):
        pass

    exchange: Union[str, None] = None
    spot_api_url: Union[str, None] = None
    futures_api_url: Union[str, None] = None
    weight: int = 0
    max_weight: int = 100

    def check_weight(self) -> None:
        if self.weight > self.max_weight:
            log.info(
                f"Weight {self.weight} is greater than {self.max_weight}, sleeping for 60 seconds"
            )
            time.sleep(60)

    def update_weight(self, weight: int) -> None:
        self.weight = weight

    def get_spot_price(
        self, base: Union[str, None] = None, quote: Union[str, None] = None
    ) -> Decimal:
        return Decimal(-1.0)

    def get_spot_prices(self) -> list:
        return []

    def get_spot_kline(
        self,
        symbol: str,
        interval: Intervals,
        start_time: Union[int, None] = None,
        end_time: Union[int, None] = None,
        limit: int = 500,
    ) -> dict:
        return {}
