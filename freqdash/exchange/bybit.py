import logging
from decimal import Decimal

from freqdash.core.utils import find_in_string, send_public_request
from freqdash.exchange.exchange import Exchange
from freqdash.exchange.utils import Intervals, Settle

log = logging.getLogger(__name__)


class Bybit(Exchange):
    def __init__(self):
        super().__init__()
        log.info("Bybit initialised")

    exchange = "bybit"
    news_url = "https://announcements.bybit.com/en-US/"
    spot_api_url = "https://api.bybit.com"
    spot_trade_url = "https://www.bybit.com/en-US/trade/spot/BASE/QUOTE"
    futures_api_url = "https://api.bybit.com"
    futures_trade_url = "https://www.bybit.com/trade/usdt/BASEQUOTE"
    max_weight = 120

    def get_spot_price(self, base: str, quote: str) -> Decimal:
        self.check_weight()
        params = {"symbol": f"{base}{quote}"}
        header, raw_json = send_public_request(
            url=self.spot_api_url,
            url_path="/spot/v3/public/quote/ticker/price",
            payload=params,
        )
        if "result" in [*raw_json]:
            if "price" in [*raw_json["result"]]:
                return Decimal(raw_json["result"]["price"])
        return Decimal(-1.0)

    def get_spot_prices(self) -> list:
        self.check_weight()
        params: dict = {}
        header, raw_json = send_public_request(
            url=self.spot_api_url,
            url_path="/spot/v3/public/quote/ticker/price",
            payload=params,
        )
        if "result" in [*raw_json]:
            if "list" in [*raw_json["result"]]:
                return [
                    {"symbol": pair["symbol"], "price": Decimal(pair["price"])}
                    for pair in raw_json["result"]["list"]
                ]
        return []

    def get_spot_kline(
        self,
        base: str,
        quote: str,
        interval: Intervals = Intervals.ONE_DAY,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int = 500,
    ) -> list:
        self.check_weight()
        params = {"symbol": f"{base}{quote}", "interval": interval, "limit": limit}
        if start_time is not None:
            params["startTime"] = start_time
        if end_time is not None:
            params["endTime"] = end_time

        header, raw_json = send_public_request(
            url=self.spot_api_url,
            url_path="/spot/v3/public/quote/kline",
            payload=params,
        )
        if "result" in [*raw_json]:
            if "list" in [*raw_json["result"]]:
                if len(raw_json["result"]["list"]) > 0:
                    return [
                        {
                            "timestamp": int(candle["t"]),
                            "open": Decimal(candle["o"]),
                            "high": Decimal(candle["h"]),
                            "low": Decimal(candle["l"]),
                            "close": Decimal(candle["c"]),
                            "volume": Decimal(candle["v"]),
                        }
                        for candle in raw_json["result"]["list"]
                    ]
        return []

    def get_futures_price(self, base: str, quote: str) -> Decimal:
        self.check_weight()
        params = {"symbol": f"{base}{quote}"}
        header, raw_json = send_public_request(
            url=self.futures_api_url,
            url_path="/v2/public/tickers",
            payload=params,
        )
        if "result" in [*raw_json]:
            if len(raw_json["result"]) > 0:
                if "last_price" in [*raw_json["result"][0]]:
                    return Decimal(raw_json["result"][0]["last_price"])
        return Decimal(-1.0)

    def get_futures_prices(self) -> list:
        self.check_weight()
        params: dict = {}
        header, raw_json = send_public_request(
            url=self.futures_api_url,
            url_path="/v2/public/tickers",
            payload=params,
        )
        if "result" in [*raw_json]:
            return [
                {"symbol": pair["symbol"], "price": Decimal(pair["last_price"])}
                for pair in raw_json["result"]
            ]
        return []

    def get_futures_kline(
        self,
        base: str,
        quote: str,
        start_time: int,
        end_time: int | None = None,
        interval: Intervals = Intervals.ONE_DAY,
        limit: int = 200,
        settle: Settle | None = None,
    ) -> list:
        self.check_weight()
        custom_intervals = {
            "1m": 1,
            "5m": 5,
            "15m": 15,
            "1h": 60,
            "4h": 240,
            "1d": "D",
            "1w": "W",
        }
        params = {
            "symbol": f"{base}{quote}",
            "interval": custom_intervals[interval],
            "limit": limit,
            "from": start_time,
        }

        header, raw_json = send_public_request(
            url=self.futures_api_url,
            url_path="/public/linear/kline",
            payload=params,
        )

        if "result" in [*raw_json]:
            if len(raw_json["result"]) > 0:
                if end_time is not None:
                    return [
                        {
                            "timestamp": int(candle["open_time"]),
                            "open": Decimal(candle["open"]),
                            "high": Decimal(candle["high"]),
                            "low": Decimal(candle["low"]),
                            "close": Decimal(candle["close"]),
                            "volume": Decimal(candle["volume"]),
                        }
                        for candle in raw_json["result"]
                        if int(candle["open_time"]) <= end_time
                    ]
                return [
                    {
                        "timestamp": int(candle["open_time"]),
                        "open": Decimal(candle["open"]),
                        "high": Decimal(candle["high"]),
                        "low": Decimal(candle["low"]),
                        "close": Decimal(candle["close"]),
                        "volume": Decimal(candle["volume"]),
                    }
                    for candle in raw_json["result"]
                ]
        return []

    def get_news(self) -> list:
        all_categories = [
            "new_crypto",
            "latest_activities",
            "latest_bybit_news",
            "product_updates",
            "new_fiat_listings",
            "maintenance_updates",
            "delistings",
            "other",
        ]
        news_type = {
            "new_crypto": "New crypto",
            "latest_bybit_news": "Latest news",
            "latest_activities": "Latest activities",
            "new_fiat_listings": "New fiat",
            "delistings": "Delisting",
            "product_updates": "Product",
            "maintenance_updates": "API",
            "other": "Other",
        }
        news: list = []
        for category in all_categories:
            params: dict = {"category": category, "page": 1}
            header, raw_text = send_public_request(
                url=self.news_url, payload=params, json=False
            )
            to_find_start = '<script id="__NEXT_DATA__" type="application/json">'
            to_find_end = "</script>"

            text = find_in_string(
                string=raw_text,
                start_substring=to_find_start,
                end_substring=to_find_end,
                return_json=True,
            )
            if len(text) > 0:
                if "props" in text:
                    if "pageProps" in text["props"]:
                        if "articleInitEntity" in text["props"]["pageProps"]:
                            if (
                                "list"
                                in text["props"]["pageProps"]["articleInitEntity"]
                            ):
                                for item in text["props"]["pageProps"][
                                    "articleInitEntity"
                                ]["list"]:
                                    headline = item["title"]
                                    release = item["date_timestamp"] * 1000
                                    code = item["url"]
                                    news.append(
                                        {
                                            "headline": headline,
                                            "category": news_type[category],
                                            "hyperlink": f"{self.news_url}{code}",
                                            "news_time": release,
                                        }
                                    )
        return news
