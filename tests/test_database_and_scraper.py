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
        assert self.scraper.get_jwt_token(self.scraper.tunnels[0]) == "test"
        send_post.return_value = ["header", {}]
        assert self.scraper.get_jwt_token(self.scraper.tunnels[0]) == "no_jwt_retrieved"

    @patch("freqdash.scraper.scraper.send_public_request")
    def test_scraper(self, send_post):
        send_post.return_value = ["header", {}]
        assert self.scraper.get_config(self.scraper.tunnels[0]) == {}
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
        config = self.scraper.get_config(self.scraper.tunnels[0])
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
        assert self.scraper.get_sysinfo(self.scraper.tunnels[0]) == {}

        send_post.return_value = ["header", {"cpu_pct": [5, 6], "ram_pct": 5}]
        sysinfo = self.scraper.get_sysinfo(self.scraper.tunnels[0])
        assert sysinfo == {
            "cpu_pct": "5,6",
            "ram_pct": 5,
        }
        data = {"host_id": result} | sysinfo
        self.database.add_sysinfo(data=data)
        assert self.database.get_oldest_open_trade_id(host_id=result) == 0


if __name__ == "__main__":
    unittest.main()
