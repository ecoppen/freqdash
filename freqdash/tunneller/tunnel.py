import logging

from sshtunnel import SSHTunnelForwarder

from freqdash.core.config import FreqtradeAPI

log = logging.getLogger(__name__)


class Tunnel:
    def __init__(self, instance: FreqtradeAPI) -> None:
        self.ssh_host = str(instance.ssh_host)
        self.ssh_port = instance.ssh_port
        self.ssh_address = f"{self.ssh_host}:{self.ssh_port}"
        self.api_username = instance.api_username
        self.api_password = instance.api_password
        self.started = False
        self.local_bind_port = None

        self.server = SSHTunnelForwarder(
            (self.ssh_host, self.ssh_port),
            ssh_username=instance.ssh_username,
            ssh_password=instance.ssh_password,
            remote_bind_address=(str(instance.remote_host), instance.remote_port),
        )
        log.info(
            f"Tunnel instance {instance.ssh_host}:{instance.ssh_port} initialised "
        )

    def start(self):
        self.server.start()
        self.local_bind_port = self.server.local_bind_port
        log.info(
            f"Tunnel started to {self.ssh_address} and locally bound to port {self.local_bind_port}"
        )

    def stop(self):
        self.server.stop()
        log.info(f"Tunnel stopped to {self.ssh_address}")
        self.local_bind_port = None
