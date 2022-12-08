import logging

import requests  # type: ignore

from freqdash.core.utils import send_public_request

log = logging.getLogger(__name__)


class Scraper:
    def __init__(self, tunnels, database) -> None:
        self.tunnels = tunnels
        self.database = database

    def scrape(self) -> None:
        try:
            self.scrape_cycle()
        except requests.exceptions.Timeout:
            log.warning("Request timed out")
        except requests.exceptions.TooManyRedirects:
            log.warning("Too many redirects")
        except requests.exceptions.RequestException as e:
            log.warning(f"Request exception: {e}")

    def scrape_cycle(self) -> None:
        for tunnel in self.tunnels:
            tunnel.start()
            config = self.get_config(tunnel=tunnel)
            if config:
                log.info(f"Scraped {config['host']}")
                result = self.database.check_then_add_or_update_host(data=config)
                sysinfo = self.get_sysinfo(tunnel=tunnel)
                if sysinfo:
                    data = {"host_id": result} | sysinfo
                    self.database.add_sysinfo(data=data)
                last_open_trade_id = self.database.get_oldest_open_trade_id(
                    host_id=result
                )
                log.info(f"last open trade id = {last_open_trade_id}")
                closed_trades = self.get_closed_trades(
                    tunnel=tunnel, offset=last_open_trade_id
                )
                log.info(closed_trades)
                self.database.check_then_add_trades(data=closed_trades, host_id=result)
                open_trades = self.get_open_trades(tunnel=tunnel)
                self.database.check_then_add_trades(data=open_trades, host_id=result)

            tunnel.stop()

    def get_config(self, tunnel) -> dict:
        basepath = f"http://{tunnel.remote_host}:{tunnel.local_bind_port}/api/v1/"
        headers, json = send_public_request(
            url=basepath + "show_config",
            method="GET",
            auth=(tunnel.api_username, tunnel.api_password),
        )
        data: dict = {}
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

    def get_sysinfo(self, tunnel) -> dict:
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

    def get_closed_trades(self, tunnel, offset: int = 0) -> list:
        basepath = f"http://{tunnel.remote_host}:{tunnel.local_bind_port}/api/v1/"
        headers, json = send_public_request(
            url=basepath + "trades",
            payload={"limit": 500, "offset": offset},
            method="GET",
            auth=(tunnel.api_username, tunnel.api_password),
        )
        return json["trades"]

    def get_open_trades(self, tunnel) -> list:
        basepath = f"http://{tunnel.remote_host}:{tunnel.local_bind_port}/api/v1/"
        headers, json = send_public_request(
            url=basepath + "status",
            method="GET",
            auth=(tunnel.api_username, tunnel.api_password),
        )
        return json
