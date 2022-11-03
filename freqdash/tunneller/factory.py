import logging

from freqdash.tunneller.tunnel import Tunnel

log = logging.getLogger(__name__)


def load_tunnels(config: list) -> list:
    tunnels: list = []
    for instance in config:
        tunnels.append(Tunnel(instance))
    return tunnels
