import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import requests  # type: ignore

from freqdash.connection.tunnel import Tunnel
from freqdash.core.config import RemoteFreqtradeAPI
from freqdash.models.database import Database
from freqdash.scraper.scraper import Scraper


class TestScraper(unittest.TestCase):
    path = Path(":memory:")
    database = Database(path=path)

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
    def test_scraper_get_config(self, send_post):
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
        assert self.scraper.get_config(self.scraper.tunnels[0]) == {
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
        send_post.return_value = ["header", {}]
        assert self.scraper.get_config(self.scraper.tunnels[0]) == {}

    @patch("freqdash.scraper.scraper.send_public_request")
    def test_scraper_get_sysinfo(self, send_post):
        send_post.return_value = ["header", {"cpu_pct": [5, 6], "ram_pct": 5}]
        assert self.scraper.get_sysinfo(self.scraper.tunnels[0]) == {
            "cpu_pct": "5,6",
            "ram_pct": 5,
        }
        send_post.return_value = ["header", {}]
        assert self.scraper.get_sysinfo(self.scraper.tunnels[0]) == {}


if __name__ == "__main__":
    unittest.main()
