import unittest

import requests  # type: ignore

from freqdash.exchange.gateio import Gateio


class TestBybitExchange(unittest.TestCase):
    def test_attributes(self):
        gateio = Gateio()
        assert gateio.exchange == "gateio"
        assert gateio.spot_api_url == "https://api.gateio.ws"
        assert gateio.spot_trade_url == "https://www.gate.io/trade/BASE_QUOTE"
        assert gateio.futures_api_url == "https://api.gateio.ws"
        assert (
            gateio.futures_trade_url
            == "https://www.gate.io/futures_trade/USDT/BASE_QUOTE"
        )
        assert gateio.weight == 0
        assert gateio.max_weight == 1000


if __name__ == "__main__":
    unittest.main()
