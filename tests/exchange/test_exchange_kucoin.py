import unittest

import requests  # type: ignore

from freqdash.exchange.kucoin import Kucoin


class TestBybitExchange(unittest.TestCase):
    def test_attributes(self):
        kucoin = Kucoin()
        assert kucoin.exchange == "kucoin"
        assert kucoin.spot_api_url == "https://api.kucoin.com"
        assert kucoin.spot_trade_url == "https://www.kucoin.com/trade/BASE-QUOTE"
        assert kucoin.futures_api_url == "https://api-futures.kucoin.com"
        assert (
            kucoin.futures_trade_url == "https://www.kucoin.com/futures/trade/BASEQUOTE"
        )
        assert kucoin.weight == 0
        assert kucoin.max_weight == 600


if __name__ == "__main__":
    unittest.main()
