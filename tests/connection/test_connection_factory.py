import unittest
from pathlib import Path

from freqdash.connection.factory import load_tunnels
from freqdash.core.config import RemoteFreqtradeAPI


class TestCoreConfig(unittest.TestCase):
    def test_load_tunnels(self):
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

        tunnels = load_tunnels(
            config=[remote_freqtrade_api], ssh_keys_folder=ssh_keys_folder
        )

        assert tunnels[0].ssh_host == "127.0.0.1"
        assert tunnels[0].ssh_port == 1
        assert tunnels[0].ssh_address == "127.0.0.1:1"
        assert tunnels[0].ssh_username == "test_ssh_username"
        assert tunnels[0].ssh_pkey_filename is None
        assert tunnels[0].ssh_password == "test_ssh_password"
        assert tunnels[0].remote_host == "127.0.0.2"
        assert tunnels[0].remote_port == 2
        assert tunnels[0].api_username == "test_api_username"
        assert tunnels[0].api_password == "test_api_password"

        assert tunnels[0].server.ssh_host == "127.0.0.1"
        assert tunnels[0].server.ssh_username == "test_ssh_username"
        assert tunnels[0].server.ssh_password == "test_ssh_password"
        assert tunnels[0].server._remote_binds == [("127.0.0.2", 2)]

    def test_load_no_tunnels(self):

        ssh_keys_folder = Path("ssh_keys")

        tunnels = load_tunnels(config=[], ssh_keys_folder=ssh_keys_folder)

        assert tunnels == []


if __name__ == "__main__":
    unittest.main()
