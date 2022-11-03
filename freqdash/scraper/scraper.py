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
            basepath = f"http://127.0.0.1:{tunnel.local_bind_port}/api/v1/"
            headers, status = send_public_request(
                url=basepath + "health",
                method="GET",
                auth=(tunnel.api_username, tunnel.api_password),
            )
            log.info(status)
            tunnel.stop()
