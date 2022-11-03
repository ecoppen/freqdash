import logging
from pathlib import Path

from freqdash.core.config import load_config
from freqdash.core.utils import send_public_request
from freqdash.tunneller.tunnel import Tunnel

log = logging.getLogger(__name__)

config_path = Path(Path().resolve(), "config", "config.json")
config = load_config(config_path)


def load_tunnels(config: list) -> list:
    tunnels: list = []
    for instance in config:
        tunnels.append(Tunnel(instance))
    return tunnels
