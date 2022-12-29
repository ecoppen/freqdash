import unittest
from decimal import Decimal

import requests  # type: ignore
import responses

from freqdash.exchange.bybit import Bybit
from freqdash.exchange.utils import Intervals


class TestBybitExchange(unittest.TestCase):
    def test_attributes(self):
        bybit = Bybit()
        assert bybit.exchange == "bybit"
        assert bybit.spot_api_url == "https://api.bybit.com"
        assert (
            bybit.spot_trade_url == "https://www.bybit.com/en-US/trade/spot/BASE/QUOTE"
        )
        assert bybit.futures_api_url == "https://api.bybit.com"
        assert bybit.futures_trade_url == "https://www.bybit.com/trade/usdt/BASEQUOTE"
        assert bybit.weight == 0
        assert bybit.max_weight == 120

    @responses.activate
    def test_get_spot_price_valid(self):
        bybit = Bybit()
        responses.get(
            url=f"{bybit.spot_api_url}/spot/v3/public/quote/ticker/price?symbol=BTCUSDT",
            body='{"retCode":0,"retMsg":"OK","result":{"symbol":"BTCUSDT","price":"16599.59"},"retExtInfo":{},"time":1672314240375}',
            status=200,
            content_type="application/json",
        )
        spot_price = bybit.get_spot_price(base="BTC", quote="USDT")
        assert spot_price == Decimal("16599.59")

    @responses.activate
    def test_get_spot_price_invalid(self):
        bybit = Bybit()
        responses.get(
            url=f"{bybit.spot_api_url}/spot/v3/public/quote/ticker/price?symbol=BTCUSDT",
            body="{}",
            status=200,
            content_type="application/json",
        )
        spot_price = bybit.get_spot_price(base="BTC", quote="USDT")
        assert spot_price == Decimal(-1.0)

    @responses.activate
    def test_get_spot_prices_valid(self):
        bybit = Bybit()
        responses.get(
            url=f"{bybit.spot_api_url}/spot/v3/public/quote/ticker/price",
            body='{"retCode":0,"retMsg":"OK","result":{"list":[{"symbol":"SAITAMAUSDT","price":0.0010585},{"symbol":"MANABTC","price":1.831e-05}]}}',
            status=200,
            content_type="application/json",
        )
        spot_prices = bybit.get_spot_prices()
        assert spot_prices == [
            {"symbol": "SAITAMAUSDT", "price": Decimal(0.0010585)},
            {"symbol": "MANABTC", "price": Decimal(1.831e-05)},
        ]

    @responses.activate
    def test_get_spot_prices_invalid(self):
        bybit = Bybit()
        responses.get(
            url=f"{bybit.spot_api_url}/spot/v3/public/quote/ticker/price",
            body="{}",
            status=200,
            content_type="application/json",
        )
        spot_prices = bybit.get_spot_prices()
        assert spot_prices == []

    @responses.activate
    def test_get_futures_price_valid(self):
        bybit = Bybit()
        responses.get(
            url=f"{bybit.futures_api_url}/v2/public/tickers?symbol=BTCUSDT",
            body='{"ret_code":0,"ret_msg":"OK","result":[{"symbol":"BTCUSDT","bid_price":"16646","ask_price":"16646.5","last_price":"16646.50","last_tick_direction":"ZeroPlusTick","prev_price_24h":"16694.00","price_24h_pcnt":"-0.002845","high_price_24h":"16778.00","low_price_24h":"16469.50","prev_price_1h":"16637.50","mark_price":"16641.41","index_price":"16641.43","open_interest":73514.77499999,"countdown_hour":0,"turnover_24h":"1559065108.6355028","volume_24h":93945.62499999,"funding_rate":"0.0001","predicted_funding_rate":"","next_funding_time":"2022-12-29T16:00:00Z","predicted_delivery_price":"","total_turnover":"","total_volume":0,"delivery_fee_rate":"","delivery_time":"","price_1h_pcnt":"","open_value":""}],"ext_code":"","ext_info":"","time_now":"1672324738.823984"}',
            status=200,
            content_type="application/json",
        )
        futures_price = bybit.get_futures_price(base="BTC", quote="USDT")
        assert futures_price == Decimal("16646.50")

    @responses.activate
    def test_get_futures_price_invalid(self):
        bybit = Bybit()
        responses.get(
            url=f"{bybit.futures_api_url}/fapi/v1/ticker/price?symbol=BTCUSDT",
            body="{}",
            status=200,
            content_type="application/json",
        )
        futures_price = bybit.get_futures_price(base="BTC", quote="USDT")
        assert futures_price == Decimal(-1.0)

    @responses.activate
    def test_get_futures_prices_valid(self):
        bybit = Bybit()
        responses.get(
            url=f"{bybit.futures_api_url}/v2/public/tickers",
            body='{"ret_code":0,"ret_msg":"OK","result":[{"symbol":"10000NFTUSDT","bid_price":"0.004375","ask_price":"0.00438","last_price":"0.004380","last_tick_direction":"PlusTick","prev_price_24h":"0.004380","price_24h_pcnt":"0","high_price_24h":"0.004435","low_price_24h":"0.004365","prev_price_1h":"0.004375","mark_price":"0.004380","index_price":"0.004381","open_interest":6.250001e+07,"countdown_hour":0,"turnover_24h":"62090.89852998","volume_24h":1.413381e+07,"funding_rate":"0.0001","predicted_funding_rate":"","next_funding_time":"2022-12-29T16:00:00Z","predicted_delivery_price":"","total_turnover":"","total_volume":0,"delivery_fee_rate":"","delivery_time":"","price_1h_pcnt":"","open_value":""},{"symbol":"1000BTTUSDT","bid_price":"0.000617","ask_price":"0.000618","last_price":"0.000617","last_tick_direction":"ZeroMinusTick","prev_price_24h":"0.000619","price_24h_pcnt":"-0.003231","high_price_24h":"0.000626","low_price_24h":"0.000614","prev_price_1h":"0.000618","mark_price":"0.000617","index_price":"0.000617","open_interest":3.085573e+08,"countdown_hour":0,"turnover_24h":"49266.629","volume_24h":7.97661e+07,"funding_rate":"0.0001","predicted_funding_rate":"","next_funding_time":"2022-12-29T16:00:00Z","predicted_delivery_price":"","total_turnover":"","total_volume":0,"delivery_fee_rate":"","delivery_time":"","price_1h_pcnt":"","open_value":""}]}',
            status=200,
            content_type="application/json",
        )
        futures_prices = bybit.get_futures_prices()
        assert futures_prices == [
            {"symbol": "10000NFTUSDT", "price": Decimal("0.004380")},
            {"symbol": "1000BTTUSDT", "price": Decimal("0.000617")},
        ]

    @responses.activate
    def test_get_futures_prices_invalid(self):
        bybit = Bybit()
        responses.get(
            url=f"{bybit.futures_api_url}/v2/public/tickers",
            body="{}",
            status=200,
            content_type="application/json",
        )
        futures_prices = bybit.get_futures_prices()
        assert futures_prices == []

    @responses.activate
    def test_get_spot_kline_valid(self):
        bybit = Bybit()
        responses.get(
            url=f"{bybit.spot_api_url}/spot/v3/public/quote/kline?symbol=BTCUSDT&interval=1d&limit=500&startTime=1632009600000&endTime=1632182400000",
            body='{"retCode":0,"retMsg":"OK","result":{"list":[{"t":1632009600000,"s":"BTCUSDT","sn":"BTCUSDT","c":"47252.31","h":"48328.8","l":"46864.83","o":"48272.38","v":"180.834669"},{"t":1632096000000,"s":"BTCUSDT","sn":"BTCUSDT","c":"43049.82","h":"47338.82","l":"42523.37","o":"47252.31","v":"531.465973"},{"t":1632182400000,"s":"BTCUSDT","sn":"BTCUSDT","c":"40717.22","h":"43600.3","l":"39632.1","o":"43049.82","v":"768.442768"}]},"retExtInfo":{},"time":1672325209525}',
            status=200,
            content_type="application/json",
        )
        spot_kline = bybit.get_spot_kline(
            base="BTC",
            quote="USDT",
            start_time=1632009600000,
            end_time=1632182400000,
            interval=Intervals.ONE_DAY,
            limit=500,
        )
        assert spot_kline == [
            {
                "timestamp": 1632009600000,
                "open": Decimal("48272.38"),
                "high": Decimal("48328.8"),
                "low": Decimal("46864.83"),
                "close": Decimal("47252.31"),
                "volume": Decimal("180.834669"),
            },
            {
                "timestamp": 1632096000000,
                "open": Decimal("47252.31"),
                "high": Decimal("47338.82"),
                "low": Decimal("42523.37"),
                "close": Decimal("43049.82"),
                "volume": Decimal("531.465973"),
            },
            {
                "timestamp": 1632182400000,
                "open": Decimal("43049.82"),
                "high": Decimal("43600.3"),
                "low": Decimal("39632.1"),
                "close": Decimal("40717.22"),
                "volume": Decimal("768.442768"),
            },
        ]

    @responses.activate
    def test_get_spot_kline_invalid(self):
        bybit = Bybit()
        responses.get(
            url=f"{bybit.futures_api_url}/spot/v3/public/quote/kline?symbol=BTCUSDT&interval=1d&limit=500&startTime=1632009600000&endTime=1632182400000",
            body="{}",
            status=200,
            content_type="application/json",
        )
        spot_kline = bybit.get_spot_kline(
            base="BTC",
            quote="USDT",
            start_time=1632009600000,
            end_time=1632182400000,
            interval=Intervals.ONE_DAY,
            limit=500,
        )
        assert spot_kline == []

    @responses.activate
    def test_get_futures_kline_valid(self):
        bybit = Bybit()
        responses.get(
            url=f"{bybit.futures_api_url}/public/linear/kline?symbol=BTCUSDT&interval=D&limit=3&from=1632009600",
            body='{"ret_code":0,"ret_msg":"OK","ext_code":"","ext_info":"","result":[{"id":12501243,"symbol":"BTCUSDT","period":"D","interval":"D","start_at":1632009600,"open_time":1632009600,"volume":34445.799,"open":48300,"high":48340.5,"low":46880,"close":47274.5,"turnover":1628407924.8255},{"id":12566235,"symbol":"BTCUSDT","period":"D","interval":"D","start_at":1632096000,"open_time":1632096000,"volume":91656.427,"open":47274.5,"high":47342,"low":42500,"close":43057,"turnover":3946450777.339},{"id":12631266,"symbol":"BTCUSDT","period":"D","interval":"D","start_at":1632182400,"open_time":1632182400,"volume":102692.021,"open":43057,"high":43600,"low":39520,"close":40724.5,"turnover":4182081209.2145}],"time_now":"1672326571.664846"}',
            status=200,
            content_type="application/json",
        )
        futures_kline = bybit.get_futures_kline(
            base="BTC",
            quote="USDT",
            start_time=1632009600,
            interval=Intervals.ONE_DAY,
            limit=3,
        )
        assert futures_kline == [
            {
                "timestamp": 1632009600,
                "open": Decimal("48300"),
                "high": Decimal("48340.5"),
                "low": Decimal("46880"),
                "close": Decimal("47274.5"),
                "volume": Decimal(34445.799),
            },
            {
                "timestamp": 1632096000,
                "open": Decimal("47274.5"),
                "high": Decimal("47342"),
                "low": Decimal("42500"),
                "close": Decimal("43057"),
                "volume": Decimal(91656.427),
            },
            {
                "timestamp": 1632182400,
                "open": Decimal("43057"),
                "high": Decimal("43600"),
                "low": Decimal("39520"),
                "close": Decimal("40724.5"),
                "volume": Decimal(102692.021),
            },
        ]

    @responses.activate
    def test_get_futures_kline_invalid(self):
        bybit = Bybit()
        responses.get(
            url=f"{bybit.futures_api_url}/public/linear/kline?symbol=BTCUSDT&interval=D&limit=3&from=1632009600",
            body="{}",
            status=200,
            content_type="application/json",
        )
        futures_kline = bybit.get_futures_kline(
            base="BTC",
            quote="USDT",
            start_time=1632009600000,
            interval=Intervals.ONE_DAY,
            limit=3,
        )
        assert futures_kline == []


if __name__ == "__main__":
    unittest.main()
