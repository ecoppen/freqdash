import logging
import time
from typing import Union

log = logging.getLogger(__name__)


class Exchange:
    def __init__(self):
        pass

    exchange: Union[str, None] = None
    spot_api_url: Union[str, None] = None
    futures_api_url: Union[str, None] = None
    weight: int = 0
    max_weight: int = 100

    def check_weight(self):
        if self.weight > self.max_weight:
            log.info(
                f"Weight {self.weight} is greater than {self.max_weight}, sleeping for 60 seconds"
            )
            time.sleep(60)

    def update_weight(self, weight: int) -> None:
        self.weight = weight

    def get_spot_prices(self):
        pass

    def get_spot_kline(
        self, symbol, interval="1d", start_time=None, end_time=None, limit=500
    ):
        pass
