import unittest
from pathlib import Path

from freqdash.connection.tunnel import Tunnel
from freqdash.core.config import RemoteFreqtradeAPI


class TestCoreConfig(unittest.TestCase):
    def test_RemoteFreqtrade_no_pkey(self):
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

        assert tunnel.ssh_host == "127.0.0.1"
        assert tunnel.ssh_port == 1
        assert tunnel.ssh_address == "127.0.0.1:1"
        assert tunnel.ssh_username == "test_ssh_username"
        assert tunnel.ssh_pkey_filename is None
        assert tunnel.ssh_password == "test_ssh_password"
        assert tunnel.remote_host == "127.0.0.2"
        assert tunnel.remote_port == 2
        assert tunnel.api_username == "test_api_username"
        assert tunnel.api_password == "test_api_password"

        assert tunnel.server.ssh_host == "127.0.0.1"
        assert tunnel.server.ssh_username == "test_ssh_username"
        assert tunnel.server.ssh_password == "test_ssh_password"
        assert tunnel.server._remote_binds == [("127.0.0.2", 2)]


if __name__ == "__main__":
    unittest.main()
