import unittest
from decimal import Decimal

import requests  # type: ignore
import responses

from freqdash.exchange.kucoin import Kucoin
from freqdash.exchange.utils import Intervals


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

    @responses.activate
    def test_get_spot_price_valid(self):
        kucoin = Kucoin()
        responses.get(
            url=f"{kucoin.spot_api_url}/api/v1/market/orderbook/level1?symbol=BTC-USDT",
            body='{"code":"200000","data":{"time":1672585428412,"sequence":"4400250097","price":"16542.7","size":"0.00001554","bestBid":"16542.7","bestBidSize":"1.96581687","bestAsk":"16542.8","bestAskSize":"3.32688824"}}',
            status=200,
            content_type="application/json",
        )
        spot_price = kucoin.get_spot_price(base="BTC", quote="USDT")
        assert spot_price == Decimal("16542.7")

    @responses.activate
    def test_get_spot_price_invalid(self):
        kucoin = Kucoin()
        responses.get(
            url=f"{kucoin.spot_api_url}/api/v1/market/orderbook/level1?symbol=BTC-USDT",
            body="",
            status=200,
            content_type="application/json",
        )
        spot_price = kucoin.get_spot_price(base="BTC", quote="USDT")
        assert spot_price == Decimal(-1.0)

    @responses.activate
    def test_get_spot_prices_valid(self):
        kucoin = Kucoin()
        responses.get(
            url=f"{kucoin.spot_api_url}/api/v1/market/allTickers",
            body='{"code":"200000","data":{"time":1672585595001,"ticker":[{"symbol":"NKN-USDT","symbolName":"NKN-USDT","buy":"0.079375","sell":"0.07966","changeRate":"-0.0004","changePrice":"-0.000039","high":"0.079662","low":"0.078361","vol":"70811.9958","volValue":"5582.1354108166","last":"0.079414","averagePrice":"0.07888563","takerFeeRate":"0.001","makerFeeRate":"0.001","takerCoefficient":"1","makerCoefficient":"1"},{"symbol":"LOOM-BTC","symbolName":"LOOM-BTC","buy":"0.000002421","sell":"0.000002442","changeRate":"-0.0113","changePrice":"-0.000000028","high":"0.000002501","low":"0.000002303","vol":"97895.8904","volValue":"0.2347530766879","last":"0.000002432","averagePrice":"0.00000237","takerFeeRate":"0.001","makerFeeRate":"0.001","takerCoefficient":"1","makerCoefficient":"1"}]}}',
            status=200,
            content_type="application/json",
        )
        spot_prices = kucoin.get_spot_prices()
        assert spot_prices == [
            {"symbol": "NKNUSDT", "price": Decimal("0.079414")},
            {"symbol": "LOOMBTC", "price": Decimal("0.000002432")},
        ]

    @responses.activate
    def test_get_spot_prices_invalid(self):
        kucoin = Kucoin()
        responses.get(
            url=f"{kucoin.spot_api_url}/api/v1/market/allTickers",
            body="{}",
            status=200,
            content_type="application/json",
        )
        spot_prices = kucoin.get_spot_prices()
        assert spot_prices == []

    @responses.activate
    def test_get_futures_price_valid(self):
        kucoin = Kucoin()
        responses.get(
            url=f"{kucoin.futures_api_url}/api/v1/ticker?symbol=XBTUSDTM",
            body='{"code":"200000","data":{"sequence":1672297956768,"symbol":"XBTUSDTM","side":"buy","size":1,"price":"16556.0","bestBidSize":22792,"bestBidPrice":"16555.0","bestAskPrice":"16556.0","tradeId":"63b1a36900006500656859b9","ts":1672586093313562697,"bestAskSize":76638}}',
            status=200,
            content_type="application/json",
        )
        futures_price = kucoin.get_futures_price(base="XBT", quote="USDTM")
        assert futures_price == Decimal("16556.0")

    @responses.activate
    def test_get_futures_price_invalid(self):
        kucoin = Kucoin()
        responses.get(
            url=f"{kucoin.futures_api_url}/api/v1/ticker?symbol=XBTUSDTM",
            body="{}",
            status=200,
            content_type="application/json",
        )
        futures_price = kucoin.get_futures_price(base="XBT", quote="USDTM")
        assert futures_price == Decimal(-1.0)

    @responses.activate
    def test_get_futures_prices_valid(self):
        kucoin = Kucoin()
        responses.get(
            url=f"{kucoin.futures_api_url}/api/v1/contracts/active",
            body='{"code":"200000","data":[{"symbol":"XBTUSDTM","rootSymbol":"USDT","type":"FFWCSX","firstOpenDate":1585555200000,"expireDate":null,"settleDate":null,"baseCurrency":"XBT","quoteCurrency":"USDT","settleCurrency":"USDT","maxOrderQty":1000000,"maxPrice":1000000.0000000000,"lotSize":1,"tickSize":1.0,"indexPriceTickSize":0.01,"multiplier":0.001,"initialMargin":0.01,"maintainMargin":0.005,"maxRiskLimit":250000,"minRiskLimit":250000,"riskStep":125000,"makerFeeRate":0.00020,"takerFeeRate":0.00060,"takerFixFee":0.0000000000,"makerFixFee":0.0000000000,"settlementFee":null,"isDeleverage":true,"isQuanto":true,"isInverse":false,"markMethod":"FairPrice","fairMethod":"FundingRate","fundingBaseSymbol":".XBTINT8H","fundingQuoteSymbol":".USDTINT8H","fundingRateSymbol":".XBTUSDTMFPI8H","indexSymbol":".KXBTUSDT","settlementSymbol":"","status":"Open","fundingFeeRate":0.000160,"predictedFundingFeeRate":0.000109,"openInterest":"29055549","turnoverOf24h":126331950.95503426,"volumeOf24h":7633.94900000,"markPrice":16539.40,"indexPrice":16537.88,"lastTradePrice":16548.0000000000,"nextFundingRateTime":16545690,"maxLeverage":100,"sourceExchanges":["huobi","Okex","Binance","Kucoin","Poloniex","Hitbtc"],"premiumsSymbol1M":".XBTUSDTMPI","premiumsSymbol8H":".XBTUSDTMPI8H","fundingBaseSymbol1M":".XBTINT","fundingQuoteSymbol1M":".USDTINT","lowPrice":16474,"highPrice":16625,"priceChgPct":-0.0045,"priceChg":-75},{"symbol":"XBTUSDM","rootSymbol":"XBT","type":"FFWCSX","firstOpenDate":1552638575000,"expireDate":null,"settleDate":null,"baseCurrency":"XBT","quoteCurrency":"USD","settleCurrency":"XBT","maxOrderQty":10000000,"maxPrice":1000000.0000000000,"lotSize":1,"tickSize":1.0,"indexPriceTickSize":0.01,"multiplier":-1.0,"initialMargin":0.02,"maintainMargin":0.01,"maxRiskLimit":40,"minRiskLimit":40,"riskStep":20,"makerFeeRate":0.00020,"takerFeeRate":0.00060,"takerFixFee":0.0000000000,"makerFixFee":0.0000000000,"settlementFee":null,"isDeleverage":true,"isQuanto":false,"isInverse":true,"markMethod":"FairPrice","fairMethod":"FundingRate","fundingBaseSymbol":".XBTINT8H","fundingQuoteSymbol":".USDINT8H","fundingRateSymbol":".XBTUSDMFPI8H","indexSymbol":".BXBT","settlementSymbol":null,"status":"Open","fundingFeeRate":0.000100,"predictedFundingFeeRate":0.000100,"openInterest":"18157442","turnoverOf24h":68.02716403,"volumeOf24h":1124530.00000000,"markPrice":16537.95,"indexPrice":16537.00,"lastTradePrice":16532.0000000000,"nextFundingRateTime":16554795,"maxLeverage":50,"sourceExchanges":["Bitstamp","Bittrex","Coinbase","Gemini","Kraken","Liquid"],"premiumsSymbol1M":".XBTUSDMPI","premiumsSymbol8H":".XBTUSDMPI8H","fundingBaseSymbol1M":".XBTINT","fundingQuoteSymbol1M":".USDINT","lowPrice":16464,"highPrice":16604,"priceChgPct":-0.0043,"priceChg":-72}]}',
            status=200,
            content_type="application/json",
        )
        futures_prices = kucoin.get_futures_prices()
        assert futures_prices == [
            {"symbol": "XBTUSDTM", "price": Decimal(16539.40)},
            {"symbol": "XBTUSDM", "price": Decimal(16537.95)},
        ]

    @responses.activate
    def test_get_futures_prices_invalid(self):
        kucoin = Kucoin()
        responses.get(
            url=f"{kucoin.futures_api_url}/api/v1/contracts/active",
            body="{}",
            status=200,
            content_type="application/json",
        )
        futures_prices = kucoin.get_futures_prices()
        assert futures_prices == []

    @responses.activate
    def test_get_spot_kline_valid(self):
        kucoin = Kucoin()
        responses.get(
            url=f"{kucoin.spot_api_url}/api/v1/market/candles?symbol=BTC-USDT&type=1day&startAt=1632009600&endAt=1632182401",
            body='{"code":"200000","data":[["1632182400","43010.4","40730.4","43648","39571","10034.90921846","421193931.210906551"],["1632096000","47242.4","43018.6","47353.6","42470.5","10832.50206904","481199344.779460713"],["1632009600","48294","47242.5","48366.5","46816.2","3934.78015558","187339847.167268832"]]}',
            status=200,
            content_type="application/json",
        )
        spot_kline = kucoin.get_spot_kline(
            base="BTC",
            quote="USDT",
            start_time=1632009600,
            end_time=1632182400,
            interval=Intervals.ONE_DAY,
            limit=500,
        )

        assert spot_kline == [
            {
                "timestamp": 1632182400,
                "open": Decimal("43010.4"),
                "high": Decimal("43648"),
                "low": Decimal("39571"),
                "close": Decimal("40730.4"),
                "volume": Decimal("10034.90921846"),
            },
            {
                "timestamp": 1632096000,
                "open": Decimal("47242.4"),
                "high": Decimal("47353.6"),
                "low": Decimal("42470.5"),
                "close": Decimal("43018.6"),
                "volume": Decimal("10832.50206904"),
            },
            {
                "timestamp": 1632009600,
                "open": Decimal("48294"),
                "high": Decimal("48366.5"),
                "low": Decimal("46816.2"),
                "close": Decimal("47242.5"),
                "volume": Decimal("3934.78015558"),
            },
        ]

    @responses.activate
    def test_get_spot_kline_invalid(self):
        kucoin = Kucoin()
        responses.get(
            url=f"{kucoin.spot_api_url}/api/v1/market/candles?symbol=BTC-USDT&type=1day&startAt=1632009600&endAt=1632182401",
            body="",
            status=200,
            content_type="application/json",
        )
        spot_kline = kucoin.get_spot_kline(
            base="BTC",
            quote="USDT",
            start_time=1632009600,
            end_time=1632182400,
            interval=Intervals.ONE_DAY,
            limit=500,
        )

        assert spot_kline == []

    @responses.activate
    def test_get_futures_kline_valid(self):
        kucoin = Kucoin()
        responses.get(
            url=f"{kucoin.futures_api_url}/api/v1/kline/query?symbol=XBTUSDTM&granularity=1440&from=1632009600000&to=1632182400001",
            body='{"code":"200000","data":[[1632009600000,48292.0,48362.0,46860.0,47252.0,8452007],[1632096000000,47253.0,47344.0,42500.0,43025.0,26728385],[1632182400000,43019.0,43620.0,39537.0,40718.0,29655442]]}',
            status=200,
            content_type="application/json",
        )
        futures_kline = kucoin.get_futures_kline(
            base="XBT",
            quote="USDTM",
            start_time=1632009600000,
            end_time=1632182400000,
            interval=Intervals.ONE_DAY,
            limit=500,
        )

        assert futures_kline == [
            {
                "timestamp": 1632009600000,
                "open": Decimal(48292.0),
                "high": Decimal(48362.0),
                "low": Decimal(46860.0),
                "close": Decimal(47252.0),
                "volume": Decimal(8452007),
            },
            {
                "timestamp": 1632096000000,
                "open": Decimal(47253.0),
                "high": Decimal(47344.0),
                "low": Decimal(42500.0),
                "close": Decimal(43025.0),
                "volume": Decimal(26728385),
            },
            {
                "timestamp": 1632182400000,
                "open": Decimal(43019.0),
                "high": Decimal(43620.0),
                "low": Decimal(39537.0),
                "close": Decimal(40718.0),
                "volume": Decimal(29655442),
            },
        ]

    @responses.activate
    def test_get_futures_kline_invalid(self):
        kucoin = Kucoin()
        responses.get(
            url=f"{kucoin.futures_api_url}/api/v1/kline/query?symbol=XBTUSDTM&granularity=1440&from=1632009600000&to=1632182400000",
            body="",
            status=200,
            content_type="application/json",
        )
        futures_kline = kucoin.get_futures_kline(
            base="XBT",
            quote="USDTM",
            start_time=1632009600000,
            end_time=1632182400000,
            interval=Intervals.ONE_DAY,
            limit=500,
        )

        assert futures_kline == []


if __name__ == "__main__":
    unittest.main()
