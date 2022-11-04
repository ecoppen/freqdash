import logging

import requests  # type: ignore

from freqdash.core.utils import send_public_request

log = logging.getLogger(__name__)


class Scraper:
    def __init__(self, tunnels, database) -> None:
        self.tunnels = tunnels
        self.database = database

    def scrape(self):
        try:
            self.scrape_cycle()
        except requests.exceptions.Timeout:
            log.warning("Request timed out")
        except requests.exceptions.TooManyRedirects:
            log.warning("Too many redirects")
        except requests.exceptions.RequestException as e:
            log.warning(f"Request exception: {e}")

    def scrape_cycle(self):
        for tunnel in self.tunnels:
            tunnel.start()
            response = self.get_config(tunnel=tunnel)
            if response:
                log.info(f"Scraped {response['host']}")
                result = self.database.check_then_add_or_update_host(response)
                log.info(result)
            response = self.get_sysinfo(tunnel=tunnel)
            log.info(response)
            tunnel.stop()

    def get_config(self, tunnel) -> dict:
        basepath = f"http://{tunnel.remote_host}:{tunnel.local_bind_port}/api/v1/"
        headers, json = send_public_request(
            url=basepath + "show_config",
            method="GET",
            auth=(tunnel.api_username, tunnel.api_password),
        )
        data = {}
        if "version" in [*json]:
            data = {
                "host": f"{tunnel.ssh_host}:{tunnel.ssh_port}",
                "remote_host": f"{tunnel.remote_host}:{tunnel.remote_port}",
                "exchange": json["exchange"],
                "strategy": json["strategy"],
                "state": json["state"],
                "stake_currency": json["stake_currency"],
                "trading_mode": json["trading_mode"],
                "run_mode": json["runmode"],
                "ft_version": json["version"],
                "strategy_version": json["strategy_version"],
            }

        return data

    def get_sysinfo(self, tunnel):
        basepath = f"http://{tunnel.remote_host}:{tunnel.local_bind_port}/api/v1/"
        headers, json = send_public_request(
            url=basepath + "sysinfo",
            method="GET",
            auth=(tunnel.api_username, tunnel.api_password),
        )
        data = {}
        if "cpu_pct" in [*json]:
            data = {
                "cpu_pct": ",".join(str(each) for each in json["cpu_pct"]),
                "ram_pct": json["ram_pct"],
            }
        return data
