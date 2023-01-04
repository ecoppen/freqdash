import unittest
from decimal import Decimal

import requests  # type: ignore
import responses

from freqdash.exchange.gateio import Gateio
from freqdash.exchange.utils import Intervals


class TestGateioExchange(unittest.TestCase):
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

    @responses.activate
    def test_get_spot_price_valid(self):
        gateio = Gateio()
        responses.get(
            url=f"{gateio.spot_api_url}/api/v4/spot/tickers?currency_pair=BTC_USDT",
            body='[{"currency_pair":"BTC_USDT","last":"16618.2","lowest_ask":"16618.2","highest_bid":"16618.1","change_percentage":"0.28","base_volume":"3331.1019407569","quote_volume":"55137098.012875","high_24h":"16627.8","low_24h":"16470.5"}]',
            status=200,
            content_type="application/json",
        )
        spot_price = gateio.get_spot_price(base="BTC", quote="USDT")
        assert spot_price == Decimal("16618.2")

    @responses.activate
    def test_get_spot_price_invalid(self):
        gateio = Gateio()
        responses.get(
            url=f"{gateio.spot_api_url}/api/v1/market/orderbook/level1?symbol=BTC-USDT",
            body="",
            status=200,
            content_type="application/json",
        )
        spot_price = gateio.get_spot_price(base="BTC", quote="USDT")
        assert spot_price == Decimal(-1.0)

    @responses.activate
    def test_get_spot_prices_valid(self):
        gateio = Gateio()
        responses.get(
            url=f"{gateio.spot_api_url}/api/v4/spot/tickers",
            body='[{"currency_pair":"VGX_USDT","last":"0.30547","lowest_ask":"0.30597","highest_bid":"0.30453","change_percentage":"1.74","change_utc0":"2.46","change_utc8":"-0.5","base_volume":"556505.18004111","quote_volume":"168736.14732403","high_24h":"0.31084","low_24h":"0.29693"},{"currency_pair":"OOE_USDT","last":"0.015381","lowest_ask":"0.015489","highest_bid":"0.015255","change_percentage":"-1.01","change_utc0":"-2.43","change_utc8":"-0.9","base_volume":"824478.6336","quote_volume":"12792.587447698","high_24h":"0.016247","low_24h":"0.015208"}]',
            status=200,
            content_type="application/json",
        )
        spot_prices = gateio.get_spot_prices()
        assert spot_prices == [
            {"symbol": "VGXUSDT", "price": Decimal("0.30547")},
            {"symbol": "OOEUSDT", "price": Decimal("0.015381")},
        ]

    @responses.activate
    def test_get_spot_prices_invalid(self):
        gateio = Gateio()
        responses.get(
            url=f"{gateio.spot_api_url}/spot/v3/public/quote/ticker/price",
            body="[]",
            status=200,
            content_type="application/json",
        )
        spot_prices = gateio.get_spot_prices()
        assert spot_prices == []

    @responses.activate
    def test_get_futures_price_invalid(self):
        gateio = Gateio()
        responses.get(
            url=f"{gateio.futures_api_url}api/v4/futures/Settle.USDT/contracts/BTC_USDT",
            body="{}",
            status=200,
            content_type="application/json",
        )
        futures_price = gateio.get_futures_price(base="BTC", quote="USDT")
        assert futures_price == Decimal(-1.0)

    @responses.activate
    def test_get_futures_prices_invalid(self):
        gateio = Gateio()
        responses.get(
            url=f"{gateio.futures_api_url}/api/v4/futures/Settle.USDT/contracts",
            body="{}",
            status=200,
            content_type="application/json",
        )
        futures_prices = gateio.get_futures_prices()
        assert futures_prices == []

    @responses.activate
    def test_get_spot_kline_valid(self):
        gateio = Gateio()
        responses.get(
            url=f"{gateio.spot_api_url}/api/v4/spot/candlesticks?currency_pair=BTC_USDT&interval=1d&limit=500&from=1632009600&to=1632182400",
            body='[["1632009600","40407667.678275267577927032","47236.991","48362.191","46840","48296.999","848.0202116972"],["1632096000","109626902.31531487723364667419","43017.999","47325.991","42487.44","47236.991","2475.9950431578"],["1632182400","116656369.50972645187708055278","40734.169","43630.051","39605.63","43018","2774.4554767767"]]',
            status=200,
            content_type="application/json",
        )
        spot_kline = gateio.get_spot_kline(
            base="BTC",
            quote="USDT",
            start_time=1632009600,
            end_time=1632182400,
            interval=Intervals.ONE_DAY,
            limit=500,
        )
        assert spot_kline == [
            {
                "timestamp": 1632009600,
                "open": Decimal("48296.999"),
                "high": Decimal("48362.191"),
                "low": Decimal("46840"),
                "close": Decimal("47236.991"),
                "volume": Decimal("40407667.678275267577927032"),
            },
            {
                "timestamp": 1632096000,
                "open": Decimal("47236.991"),
                "high": Decimal("47325.991"),
                "low": Decimal("42487.44"),
                "close": Decimal("43017.999"),
                "volume": Decimal("109626902.31531487723364667419"),
            },
            {
                "timestamp": 1632182400,
                "open": Decimal("43018"),
                "high": Decimal("43630.051"),
                "low": Decimal("39605.63"),
                "close": Decimal("40734.169"),
                "volume": Decimal("116656369.50972645187708055278"),
            },
        ]

    @responses.activate
    def test_get_futures_kline_invalid(self):
        gateio = Gateio()
        responses.get(
            url=f"{gateio.futures_api_url}/api/v4/futures/Settle.USDT/candlesticks?contract=BTC_USDT&interval=5m&from=1632009600&to=1632182400",
            body="{}",
            status=200,
            content_type="application/json",
        )
        spot_kline = gateio.get_futures_kline(
            base="BTC",
            quote="USDT",
            start_time=1632009600,
            end_time=1632182400,
            interval=Intervals.ONE_DAY,
            limit=500,
        )
        assert spot_kline == []

    @responses.activate
    def test_get_futures_kline_settle_None(self):
        gateio = Gateio()
        responses.get(
            url=f"{gateio.futures_api_url}/api/v4/futures/Settle.USDT/candlesticks?contract=BTC_USDT&interval=5m&from=1632009600&to=1632182400",
            body="{}",
            status=200,
            content_type="application/json",
        )
        spot_kline = gateio.get_futures_kline(
            base="BTC",
            quote="USDT",
            start_time=1632009600,
            end_time=1632182400,
            interval=Intervals.ONE_DAY,
            limit=500,
            settle=None,
        )
        assert spot_kline == []


if __name__ == "__main__":
    unittest.main()
