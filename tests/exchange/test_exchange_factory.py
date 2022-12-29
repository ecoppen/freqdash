import unittest

from freqdash.exchange.factory import load_exchanges


class TestExchangeFactory(unittest.TestCase):
    def test_factory(self):
        exchanges = load_exchanges()
        assert len(exchanges) == 5
        assert [*exchanges] == ["binance", "bybit", "gateio", "kucoin", "okx"]
        for exchange in exchanges:
            assert exchange == exchanges[exchange].exchange
