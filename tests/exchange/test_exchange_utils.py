import unittest

from freqdash.exchange.utils import Exchanges, Intervals, Markets, Settle


class TestUtils(unittest.TestCase):
    def test_exchanges_dataclass(self):
        assert Exchanges.BINANCE.value == "binance"
        assert Exchanges.BYBIT.value == "bybit"
        assert Exchanges.GATEIO.value == "gateio"
        assert Exchanges.KUCOIN.value == "kucoin"
        assert Exchanges.OKX.value == "okx"

    def test_markets_dataclass(self):
        assert Markets.SPOT.value == "SPOT"
        assert Markets.FUTURES.value == "FUTURES"

    def test_intervals_dataclass(self):
        assert Intervals.ONE_MINUTE.value == "1m"
        assert Intervals.FIVE_MINUTES.value == "5m"
        assert Intervals.FIFTEEN_MINUTES.value == "15m"
        assert Intervals.ONE_HOUR.value == "1h"
        assert Intervals.FOUR_HOURS.value == "4h"
        assert Intervals.ONE_DAY.value == "1d"
        assert Intervals.ONE_WEEK.value == "1w"

    def test_settle_dataclass(self):
        assert Settle.BTC.value == "btc"
        assert Settle.USD.value == "usd"
        assert Settle.USDT.value == "usdt"


if __name__ == "__main__":
    unittest.main()
