import logging
import time
from decimal import Decimal

from freqdash.exchange.utils import Intervals, Settle

log = logging.getLogger(__name__)


class Exchange:
    def __init__(self):
        pass

    exchange: str | None = None
    spot_api_url: str | None = None
    spot_trade_url: str | None = None
    futures_api_url: str | None = None
    futures_trade_url: str | None = None
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

    def get_spot_price(self, base: str, quote: str) -> Decimal:
        return Decimal(-1.0)

    def get_spot_prices(self) -> list:
        return []

    def get_spot_kline(
        self,
        base: str,
        quote: str,
        interval: Intervals = Intervals.ONE_DAY,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int = 500,
    ) -> list:
        return []

    def get_futures_price(self, base: str, quote: str) -> Decimal:
        return Decimal(-1.0)

    def get_futures_prices(self) -> list:
        return []

    def get_futures_kline(
        self,
        base: str,
        quote: str,
        start_time: int,
        end_time: int | None = None,
        interval: Intervals = Intervals.ONE_DAY,
        limit: int = 500,
        settle: Settle | None = None,
    ) -> list:
        return []

    def get_spot_trade_url(self):
        return self.spot_trade_url

    def get_futures_trade_url(self):
        return self.futures_trade_url
