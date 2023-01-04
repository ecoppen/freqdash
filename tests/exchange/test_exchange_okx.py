import unittest
from decimal import Decimal

import requests  # type: ignore
import responses

from freqdash.exchange.okx import Okx
from freqdash.exchange.utils import Intervals


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

    @responses.activate
    def test_get_spot_price_valid(self):
        okx = Okx()
        responses.get(
            url=f"{okx.spot_api_url}/api/v5/market/ticker?instType=SPOT&instId=BTC-USDT",
            body='{"code":"0","msg":"","data":[{"instType":"SPOT","instId":"BTC-USDT","last":"16839.1","lastSz":"0.31226082","askPx":"16839.1","askSz":"5.93754444","bidPx":"16839","bidSz":"0.16038","open24h":"16659.1","high24h":"16988","low24h":"16651.7","volCcy24h":"86702682.03645192","vol24h":"5150.98223027","ts":"1672863560203","sodUtc0":"16676.8","sodUtc8":"16855.8"}]}',
            status=200,
            content_type="application/json",
        )
        spot_price = okx.get_spot_price(base="BTC", quote="USDT")
        assert spot_price == Decimal("16839.1")

    @responses.activate
    def test_get_spot_price_invalid(self):
        okx = Okx()
        responses.get(
            url=f"{okx.spot_api_url}/api/v5/market/ticker?instType=SPOT&instId=BTC-USDT",
            body="{}",
            status=200,
            content_type="application/json",
        )
        spot_price = okx.get_spot_price(base="BTC", quote="USDT")
        assert spot_price == Decimal(-1.0)

    @responses.activate
    def test_get_spot_prices_valid(self):
        bybit = Okx()
        responses.get(
            url=f"{bybit.spot_api_url}/api/v5/market/tickers?instType=SPOT",
            body='{"code":"0","msg":"","data":[{"instType":"SPOT","instId":"BCD-BTC","last":"0.000006","lastSz":"17.7045","askPx":"0.00000606","askSz":"41.2026","bidPx":"0.00000592","bidSz":"34","open24h":"0.00000585","high24h":"0.00000662","low24h":"0.00000562","volCcy24h":"0.1205","vol24h":"22176.332","ts":"1672864145005","sodUtc0":"0.00000594","sodUtc8":"0.00000594"},{"instType":"SPOT","instId":"MDT-USDT","last":"0.01941","lastSz":"356.862674","askPx":"0.01944","askSz":"10911.303029","bidPx":"0.0194","bidSz":"8118.390695","open24h":"0.01911","high24h":"0.01966","low24h":"0.01905","volCcy24h":"60824.945945","vol24h":"3130853.79066","ts":"1672864160509","sodUtc0":"0.01925","sodUtc8":"0.01955"}]}',
            status=200,
            content_type="application/json",
        )
        spot_prices = bybit.get_spot_prices()
        assert spot_prices == [
            {"symbol": "BCDBTC", "price": Decimal("0.000006")},
            {"symbol": "MDTUSDT", "price": Decimal("0.01941")},
        ]

    @responses.activate
    def test_get_spot_prices_invalid(self):
        okx = Okx()
        responses.get(
            url=f"{okx.spot_api_url}/api/v5/market/tickers?instType=SPOT",
            body="{}",
            status=200,
            content_type="application/json",
        )
        spot_prices = okx.get_spot_prices()
        assert spot_prices == []

    @responses.activate
    def test_get_futures_price_valid(self):
        okx = Okx()
        responses.get(
            url=f"{okx.futures_api_url}/api/v5/market/ticker?instId=ADA-USD-230106",
            body='{"code":"0","msg":"","data":[{"instType":"FUTURES","instId":"ADA-USD-230106","last":"0.26276","lastSz":"2","askPx":"0.26288","askSz":"16","bidPx":"0.26244","bidSz":"52","open24h":"0.25106","high24h":"0.27006","low24h":"0.25056","volCcy24h":"2480779.8191","vol24h":"65114","ts":"1672865124308","sodUtc0":"0.25287","sodUtc8":"0.26787"}]}',
            status=200,
            content_type="application/json",
        )
        futures_price = okx.get_futures_price(base="ADA", quote="USD-230106")
        assert futures_price == Decimal("0.26276")

    @responses.activate
    def test_get_futures_price_invalid(self):
        okx = Okx()
        responses.get(
            url=f"{okx.futures_api_url}/api/v5/market/ticker?instId=ADA-USD-230106",
            body="{}",
            status=200,
            content_type="application/json",
        )
        futures_price = okx.get_futures_price(base="ADA", quote="USD-230106")
        assert futures_price == Decimal(-1.0)

    @responses.activate
    def test_get_futures_prices_valid(self):
        okx = Okx()
        responses.get(
            url=f"{okx.futures_api_url}/api/v5/market/tickers?instType=FUTURES",
            body='{"code":"0","msg":"","data":[{"instType":"FUTURES","instId":"ADA-USD-230106","last":"0.26327","lastSz":"5","askPx":"0.26338","askSz":"54","bidPx":"0.26276","bidSz":"116","open24h":"0.25121","high24h":"0.27006","low24h":"0.25056","volCcy24h":"2486177.1178","vol24h":"65260","ts":"1672865290208","sodUtc0":"0.25287","sodUtc8":"0.26787"},{"instType":"FUTURES","instId":"BCH-USD-230106","last":"100.49","lastSz":"5","askPx":"100.54","askSz":"35","bidPx":"100.39","bidSz":"109","open24h":"99.2","high24h":"102.3","low24h":"98.97","volCcy24h":"6165.9459","vol24h":"62252","ts":"1672865285409","sodUtc0":"99.5","sodUtc8":"101.37"}]}',
            status=200,
            content_type="application/json",
        )
        futures_prices = okx.get_futures_prices()
        assert futures_prices == [
            {"symbol": "ADAUSD230106", "price": Decimal("0.26327")},
            {"symbol": "BCHUSD230106", "price": Decimal("100.49")},
        ]

    @responses.activate
    def test_get_futures_prices_invalid(self):
        okx = Okx()
        responses.get(
            url=f"{okx.futures_api_url}/api/v5/market/tickers?instType=FUTURES",
            body="{}",
            status=200,
            content_type="application/json",
        )
        futures_prices = okx.get_futures_prices()
        assert futures_prices == []


if __name__ == "__main__":
    unittest.main()
