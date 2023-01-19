import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import requests  # type: ignore

from freqdash.connection.tunnel import Tunnel
from freqdash.core.config import Database as DBConfig
from freqdash.core.config import RemoteFreqtradeAPI
from freqdash.models.database import Database
from freqdash.scraper.scraper import Scraper


class TestDatabaseAndScraper(unittest.TestCase):
    db = DBConfig(
        engine="sqlite", username="", password="", host="127.0.0.1", port=5432, name=""
    )
    database = Database(config=db)

    assert database.get_hosts_and_modes() == {}
    assert database.get_all_hosts() == {
        "live": {},
        "dry": {},
        "recent": [],
        "open": [],
    }
    assert (
        database.get_current_price(
            exchange="binance", symbol="BTCUSDT", trading_mode="SPOT"
        )
        is None
    )
    assert (
        database.get_prices(exchange="binance", quote="USDT", trading_mode="SPOT") == []
    )
    assert database.get_balances(host_id=1) == []
    assert database.get_trades(host_id=1) == []
    assert database.get_trades_count(host_id=1, quote_currency="USDT") == 0
    assert database.get_trade_profit(host_id=1, quote_currency="USDT") == 0.0
    assert database.get_orders_for_trade(host_id=1, trade_id=1) == []
    assert database.get_profit_factor(host_id=1, quote_currency="USDT") == 0.0
    assert database.get_oldest_open_trade_id(host_id=1) == 0

    remote_freqtrade_api = RemoteFreqtradeAPI(
        ssh_host="127.0.0.1",
        ssh_port="1",
        ssh_username="test_ssh_username",
        ssh_pkey_filename=None,
        ssh_password="test_ssh_password",
        remote_host="127.0.0.2",
        remote_port="2",
        api_username="test_api_username",
        api_password="test_api_password",
    )

    ssh_keys_folder = Path("ssh_keys")
    tunnel = Tunnel(instance=remote_freqtrade_api, ssh_keys_folder=ssh_keys_folder)

    scraper = Scraper(tunnels=[tunnel], database=database)

    for tunnel in scraper.tunnels:
        tunnel.start = MagicMock()  # type: ignore
        tunnel.local_bind_port = "5"
        tunnel.jwt = "test"

    @patch("freqdash.scraper.scraper.send_public_request")
    def test_scraper_get_jwt_token(self, send_post):
        assert self.scraper.tunnels == [self.tunnel]
        send_post.return_value = ["header", {"access_token": "test"}]
        assert self.scraper.get_jwt_token(tunnel=self.scraper.tunnels[0]) == "test"
        send_post.return_value = ["header", {}]
        assert (
            self.scraper.get_jwt_token(tunnel=self.scraper.tunnels[0])
            == "no_jwt_retrieved"
        )

    @patch("freqdash.scraper.scraper.send_public_request")
    def test_scraper(self, send_post):
        send_post.return_value = ["header", {}]
        assert self.scraper.get_config(tunnel=self.scraper.tunnels[0]) == {}
        send_post.return_value = [
            "header",
            {
                "host": "127.0.0.1:1",
                "remote_host": "127.0.0.2:2",
                "exchange": "binance",
                "strategy": "PocketRocket",
                "state": "running",
                "stake_currency": "USDT",
                "trading_mode": "spot",
                "runmode": "live",
                "version": "2022.12",
                "strategy_version": "v1.5",
            },
        ]
        config = self.scraper.get_config(tunnel=self.scraper.tunnels[0])
        assert config == {
            "host": "127.0.0.1:1",
            "remote_host": "127.0.0.2:2",
            "exchange": "binance",
            "strategy": "PocketRocket",
            "state": "running",
            "stake_currency": "USDT",
            "trading_mode": "spot",
            "run_mode": "live",
            "ft_version": "2022.12",
            "strategy_version": "v1.5",
        }
        config["trading_mode"] = config["trading_mode"].upper()
        result = self.database.check_then_add_or_update_host(data=config)
        assert result == 1
        assert self.database.get_hosts_and_modes() == {"binance": ["SPOT"]}

        send_post.return_value = ["header", {}]
        assert self.scraper.get_sysinfo(tunnel=self.scraper.tunnels[0]) == {}

        send_post.return_value = ["header", {"cpu_pct": [5, 6], "ram_pct": 5}]
        sysinfo = self.scraper.get_sysinfo(tunnel=self.scraper.tunnels[0])
        assert sysinfo == {
            "cpu_pct": "5,6",
            "ram_pct": 5,
        }
        data = {"host_id": result} | sysinfo
        self.database.add_sysinfo(data=data)
        assert self.database.get_oldest_open_trade_id(host_id=result) == 0
        send_post.return_value = [
            "header",
            {
                "trades": [
                    {
                        "trade_id": 1,
                        "pair": "SUSHI/USDT",
                        "base_currency": "SUSHI",
                        "quote_currency": "USDT",
                        "is_open": False,
                        "exchange": "binance",
                        "amount": 0.1,
                        "amount_requested": 20.43227476,
                        "stake_amount": 0.1286,
                        "max_stake_amount": 0.1286,
                        "strategy": "PocketRocket",
                        "enter_tag": "force_entry",
                        "timeframe": 1,
                        "fee_open": 0.001,
                        "fee_open_cost": 0.00012859999999999998,
                        "fee_open_currency": "SUSHI",
                        "fee_close": 0.001,
                        "fee_close_cost": 0.0264712,
                        "fee_close_currency": "USDT",
                        "open_date": "2022-12-06 12:30:06",
                        "open_timestamp": 1670329806846,
                        "open_rate": 1.286,
                        "open_rate_requested": 1.286,
                        "open_trade_value": 0.1287286,
                        "close_date": "2022-12-06 13:43:17",
                        "close_timestamp": 1670334197023,
                        "realized_profit": 0.312823,
                        "close_rate": 1.304,
                        "close_rate_requested": 1.304,
                        "close_profit": 0.01197092,
                        "close_profit_pct": 1.2,
                        "close_profit_abs": 0.312823,
                        "trade_duration_s": 4390,
                        "trade_duration": 73,
                        "profit_ratio": 0.01197092,
                        "profit_pct": 1.2,
                        "profit_abs": 0.312823,
                        "exit_reason": "trailing_stop_loss",
                        "exit_order_status": "closed",
                        "stop_loss_abs": 1.304,
                        "stop_loss_ratio": -0.005,
                        "stop_loss_pct": -0.5,
                        "stoploss_order_id": None,
                        "stoploss_last_update": None,
                        "stoploss_last_update_timestamp": None,
                        "initial_stop_loss_abs": 0.013,
                        "initial_stop_loss_ratio": -0.99,
                        "initial_stop_loss_pct": -99.0,
                        "min_rate": 1.267,
                        "max_rate": 1.31,
                        "leverage": 1.0,
                        "interest_rate": 0.0,
                        "liquidation_price": None,
                        "is_short": False,
                        "trading_mode": "spot",
                        "funding_fees": 0.0,
                        "open_order_id": None,
                        "orders": [
                            {
                                "amount": 20.4,
                                "safe_price": 1.286,
                                "ft_order_side": "buy",
                                "order_filled_timestamp": 1670329807657,
                                "ft_is_entry": True,
                                "pair": "SUSHI/USDT",
                                "order_id": "336605080",
                                "status": "closed",
                                "average": 1.286,
                                "cost": 26.2344,
                                "filled": 20.4,
                                "is_open": False,
                                "order_date": "2022-12-06 12:30:06",
                                "order_timestamp": 1670329806843,
                                "order_filled_date": "2022-12-06 12:30:07",
                                "order_type": "limit",
                                "price": 1.286,
                                "remaining": 0.0,
                            },
                            {
                                "amount": 20.3,
                                "safe_price": 1.304,
                                "ft_order_side": "sell",
                                "order_filled_timestamp": 1670334197018,
                                "ft_is_entry": False,
                                "pair": "SUSHI/USDT",
                                "order_id": "336652684",
                                "status": "closed",
                                "average": 1.304,
                                "cost": 26.4712,
                                "filled": 20.3,
                                "is_open": False,
                                "order_date": "2022-12-06 13:43:16",
                                "order_timestamp": 1670334196660,
                                "order_filled_date": "2022-12-06 13:43:17",
                                "order_type": "market",
                                "price": 1.304,
                                "remaining": 0.0,
                            },
                        ],
                    },
                    {
                        "trade_id": 2,
                        "pair": "TKO/USDT",
                        "base_currency": "TKO",
                        "quote_currency": "USDT",
                        "is_open": False,
                        "exchange": "binance",
                        "amount": 61.3,
                        "amount_requested": 61.35260619,
                        "stake_amount": 26.2977,
                        "max_stake_amount": 26.2977,
                        "strategy": "PocketRocket",
                        "enter_tag": "force_entry",
                        "timeframe": 1,
                        "fee_open": 0.001,
                        "fee_open_cost": 0.0262977,
                        "fee_open_currency": "TKO",
                        "fee_close": 0.001,
                        "fee_close_cost": 0.0266062,
                        "fee_close_currency": "USDT",
                        "open_date": "2022-12-07 13:15:11",
                        "open_timestamp": 1670418911785,
                        "open_rate": 0.429,
                        "open_rate_requested": 0.429,
                        "open_trade_value": 26.3239977,
                        "close_date": "2022-12-07 14:18:02",
                        "close_timestamp": 1670422682731,
                        "realized_profit": 0.2555961,
                        "close_rate": 0.4340326264274062,
                        "close_rate_requested": 0.435,
                        "close_profit": 0.009709623246168267,
                        "close_profit_pct": 0.97,
                        "close_profit_abs": 0.2555961,
                        "trade_duration_s": 3770,
                        "trade_duration": 62,
                        "profit_ratio": 0.009709623246168267,
                        "profit_pct": 0.97,
                        "profit_abs": 0.2555961,
                        "exit_reason": "trailing_stop_loss",
                        "exit_order_status": "closed",
                        "stop_loss_abs": 0.436,
                        "stop_loss_ratio": -0.005,
                        "stop_loss_pct": -0.5,
                        "stoploss_order_id": None,
                        "stoploss_last_update": None,
                        "stoploss_last_update_timestamp": None,
                        "initial_stop_loss_abs": 0.005,
                        "initial_stop_loss_ratio": -0.99,
                        "initial_stop_loss_pct": -99.0,
                        "min_rate": 0.422,
                        "max_rate": 0.438,
                        "leverage": 1.0,
                        "interest_rate": 0.0,
                        "liquidation_price": None,
                        "is_short": False,
                        "trading_mode": "spot",
                        "funding_fees": 0.0,
                        "open_order_id": None,
                        "orders": [
                            {
                                "amount": 61.3,
                                "safe_price": 0.429,
                                "ft_order_side": "buy",
                                "order_filled_timestamp": 1670418913081,
                                "ft_is_entry": True,
                                "pair": "TKO/USDT",
                                "order_id": "85482476",
                                "status": "closed",
                                "average": 0.429,
                                "cost": 26.2977,
                                "filled": 61.3,
                                "is_open": False,
                                "order_date": "2022-12-07 13:15:11",
                                "order_timestamp": 1670418911781,
                                "order_filled_date": "2022-12-07 13:15:13",
                                "order_type": "limit",
                                "price": 0.429,
                                "remaining": 0.0,
                            },
                            {
                                "amount": 61.3,
                                "safe_price": 0.4340326264274062,
                                "ft_order_side": "sell",
                                "order_filled_timestamp": 1670422682721,
                                "ft_is_entry": False,
                                "pair": "TKO/USDT",
                                "order_id": "85499861",
                                "status": "closed",
                                "average": 0.43403263,
                                "cost": 26.6062,
                                "filled": 61.3,
                                "is_open": False,
                                "order_date": "2022-12-07 14:18:01",
                                "order_timestamp": 1670422681936,
                                "order_filled_date": "2022-12-07 14:18:02",
                                "order_type": "market",
                                "price": 0.4340326264274062,
                                "remaining": 0.0,
                            },
                        ],
                    },
                ]
            },
        ]
        assert (
            self.database.get_trades_count(
                host_id=result, quote_currency="USDT", is_open=False
            )
            == 0
        )
        assert self.database.get_trades(host_id=result, is_open=False) == []

        closed_trades = self.scraper.get_closed_trades(
            tunnel=self.scraper.tunnels[0], offset=0
        )
        self.database.check_then_add_trades(data=closed_trades, host_id=result)
        db_closed_trades = self.database.get_trades(host_id=result, is_open=False)
        assert db_closed_trades == [
            (
                1,
                1,
                "SUSHI/USDT",
                "SUSHI",
                "USDT",
                "binance",
                False,
                0.1,
                0.1286,
                0.312823,
                "force_entry",
                0.00012859999999999998,
                "SUSHI",
                0.0264712,
                "USDT",
                1670329806846,
                1.286,
                1670334197023,
                1.304,
                "trailing_stop_loss",
                1.304,
                1.0,
                False,
                "SPOT",
                0.0,
            ),
            (
                1,
                2,
                "TKO/USDT",
                "TKO",
                "USDT",
                "binance",
                False,
                61.3,
                26.2977,
                0.2555961,
                "force_entry",
                0.0262977,
                "TKO",
                0.0266062,
                "USDT",
                1670418911785,
                0.429,
                1670422682731,
                0.4340326264274062,
                "trailing_stop_loss",
                0.436,
                1.0,
                False,
                "SPOT",
                0.0,
            ),
        ]
        count_db_closed_trades = self.database.get_trades_count(
            host_id=result, quote_currency="USDT", is_open=False
        )
        assert count_db_closed_trades == 2


if __name__ == "__main__":
    unittest.main()
