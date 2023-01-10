import logging

import requests  # type: ignore

from freqdash.core.utils import send_public_request
from freqdash.models.database import Database

log = logging.getLogger(__name__)


class Scraper:
    def __init__(self, tunnels: list, database: Database) -> None:
        self.tunnels = tunnels
        self.database = database

    def scrape(self) -> None:
        self.scrape_cycle()

    def scrape_cycle(self) -> None:
        for tunnel in self.tunnels:
            tunnel.start()
            tunnel.jwt = self.get_jwt_token(tunnel=tunnel)
            config = self.get_config(tunnel=tunnel)
            if config:
                log.info(f"Scraped {config['host']}")
                config["trading_mode"] = config["trading_mode"].upper()
                result = self.database.check_then_add_or_update_host(data=config)
                sysinfo = self.get_sysinfo(tunnel=tunnel)
                if sysinfo:
                    data = {"host_id": result} | sysinfo
                    self.database.add_sysinfo(data=data)
                last_open_trade_id = self.database.get_oldest_open_trade_id(
                    host_id=result
                )
                last_open_trade_id //= 2
                log.info(f"last open trade id = {last_open_trade_id}")
                closed_trades = self.get_closed_trades(
                    tunnel=tunnel, offset=last_open_trade_id
                )

                self.database.check_then_add_trades(data=closed_trades, host_id=result)
                open_trades = self.get_open_trades(tunnel=tunnel)
                self.database.check_then_add_trades(data=open_trades, host_id=result)

                health = self.get_health(tunnel=tunnel)
                self.database.add_last_process_ts(data=health, host_id=result)
                balance = self.get_balance(tunnel=tunnel)
                self.database.update_starting_capital(
                    data=balance["starting_capital"], host_id=result
                )
                self.database.update_balances(
                    data=balance["currencies"], host_id=result
                )
                logs = self.get_logs(tunnel=tunnel)
                self.database.update_logs(data=logs, host_id=result)
                locks = self.get_locks(tunnel=tunnel)
                log.info(locks)
                whitelist = self.get_whitelist(tunnel=tunnel)
                self.database.delete_then_add_baselist(data=whitelist, host_id=result)
                blacklist = self.get_blacklist(tunnel=tunnel)
                self.database.delete_then_add_baselist(
                    data=blacklist, host_id=result, list_type="black"
                )

            tunnel.jwt = None
            tunnel.stop()

    def get_jwt_token(self, tunnel) -> str:
        basepath = f"http://{tunnel.remote_host}:{tunnel.local_bind_port}/api/v1/"
        headers, json = send_public_request(
            url=basepath + "token/login",
            method="POST",
            auth=(tunnel.api_username, tunnel.api_password),
        )
        if "access_token" not in json:
            log.warning("No JWT retrieved")
            return "no_jwt_retrieved"
        return json["access_token"]

    def get_config(self, tunnel) -> dict:
        basepath = f"http://{tunnel.remote_host}:{tunnel.local_bind_port}/api/v1/"
        headers, json = send_public_request(
            url=basepath + "show_config",
            method="GET",
            access_token=tunnel.jwt,
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
            access_token=tunnel.jwt,
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
            access_token=tunnel.jwt,
        )
        return json["trades"]

    def get_open_trades(self, tunnel) -> list:
        basepath = f"http://{tunnel.remote_host}:{tunnel.local_bind_port}/api/v1/"
        headers, json = send_public_request(
            url=basepath + "status",
            method="GET",
            access_token=tunnel.jwt,
        )
        return json

    def get_balance(self, tunnel):
        basepath = f"http://{tunnel.remote_host}:{tunnel.local_bind_port}/api/v1/"
        headers, json = send_public_request(
            url=basepath + "balance",
            method="GET",
            access_token=tunnel.jwt,
        )
        return json

    def get_logs(self, tunnel):
        basepath = f"http://{tunnel.remote_host}:{tunnel.local_bind_port}/api/v1/"
        headers, json = send_public_request(
            url=basepath + "logs",
            method="GET",
            access_token=tunnel.jwt,
        )
        return json["logs"]

    def get_locks(self, tunnel):
        basepath = f"http://{tunnel.remote_host}:{tunnel.local_bind_port}/api/v1/"
        headers, json = send_public_request(
            url=basepath + "locks",
            method="GET",
            access_token=tunnel.jwt,
        )
        return json["locks"]

    def get_whitelist(self, tunnel):
        basepath = f"http://{tunnel.remote_host}:{tunnel.local_bind_port}/api/v1/"
        headers, json = send_public_request(
            url=basepath + "whitelist",
            method="GET",
            access_token=tunnel.jwt,
        )
        return json["whitelist"]

    def get_blacklist(self, tunnel):
        basepath = f"http://{tunnel.remote_host}:{tunnel.local_bind_port}/api/v1/"
        headers, json = send_public_request(
            url=basepath + "blacklist",
            method="GET",
            access_token=tunnel.jwt,
        )
        return json["blacklist"]

    def get_health(self, tunnel):
        basepath = f"http://{tunnel.remote_host}:{tunnel.local_bind_port}/api/v1/"
        headers, json = send_public_request(
            url=basepath + "health",
            method="GET",
            access_token=tunnel.jwt,
        )
        return json["last_process_ts"]
