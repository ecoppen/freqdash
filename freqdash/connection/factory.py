import logging
from pathlib import Path

from freqdash.connection.tunnel import Tunnel

log = logging.getLogger(__name__)


def load_tunnels(config: list, ssh_keys_folder: Path) -> list:
    tunnels: list = []
    for instance in config:
        tunnels.append(Tunnel(instance, ssh_keys_folder))
    return tunnels
