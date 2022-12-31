import unittest

import requests  # type: ignore

from freqdash.exchange.okx import Okx


class TestBybitExchange(unittest.TestCase):
    def test_attributes(self):
        okx = Okx()
        assert okx.exchange == "okx"
        assert okx.spot_api_url == "https://www.okx.com"
        assert okx.spot_trade_url == "https://www.okx.com/trade-spot/base-quote"
        assert okx.futures_api_url == "https://www.okx.com"
        assert okx.futures_trade_url == "https://www.okx.com/trade-futures/base-quote"
        assert okx.weight == 0
        assert okx.max_weight == 600


if __name__ == "__main__":
    unittest.main()
