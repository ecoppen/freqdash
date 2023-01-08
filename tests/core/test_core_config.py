import unittest
from pathlib import Path
from unittest import mock
from unittest.mock import patch

from pydantic import IPvAnyAddress, ValidationError

from freqdash.core.config import (
    Config,
    LocalFreqtradeAPI,
    RemoteFreqtradeAPI,
    load_config,
)


class TestCoreConfig(unittest.TestCase):
    def test_LocalFreqtradeAPI_valid_config(self):
        local_freqtrade_api = LocalFreqtradeAPI(
            local_host="127.0.0.1",
            local_port="1",
            api_username="test",
            api_password="test",
        )
        assert local_freqtrade_api.local_host == IPvAnyAddress.validate("127.0.0.1")
        assert local_freqtrade_api.local_port == 1
        assert local_freqtrade_api.api_username == "test"
        assert local_freqtrade_api.api_password == "test"

    def test_LocalFreqtradeAPI_invalid_port(self):
        with self.assertRaises(ValidationError):
            LocalFreqtradeAPI(
                local_host="127.0.0.1",
                local_port="0",
                api_username="test",
                api_password="test",
            )
        with self.assertRaises(ValidationError):
            LocalFreqtradeAPI(
                loca_host="127.0.0.1",
                local_port="65536",
                api_username="test",
                api_password="test",
            )

    def test_LocalFreqtradeAPI_missing_attributes(self):
        with self.assertRaises(ValidationError):
            LocalFreqtradeAPI(
                local_host="", local_port="1", api_username="test", api_password="test"
            )
        with self.assertRaises(ValidationError):
            LocalFreqtradeAPI(
                local_host="127.0.0.1",
                local_port="",
                api_username="test",
                api_password="test",
            )
        with self.assertRaises(ValidationError):
            LocalFreqtradeAPI(
                local_host="127.0.0.1",
                local_port="1",
                api_username="",
                api_password="test",
            )
        with self.assertRaises(ValidationError):
            LocalFreqtradeAPI(
                local_host="127.0.0.1",
                local_port="1",
                api_username="test",
                api_password="",
            )

    def test_RemoteFreqtradeAPI_valid_config(self):
        remote_freqtrade_api = RemoteFreqtradeAPI(
            ssh_host="127.0.0.1",
            ssh_port="1",
            ssh_username="test",
            ssh_pkey_filename="test",
            ssh_password="test",
            remote_host="127.0.0.1",
            remote_port="1",
            api_username="test",
            api_password="test",
        )
        assert remote_freqtrade_api.ssh_host == IPvAnyAddress.validate("127.0.0.1")
        assert remote_freqtrade_api.ssh_port == 1
        assert remote_freqtrade_api.ssh_username == "test"
        assert remote_freqtrade_api.ssh_pkey_filename == "test"
        assert remote_freqtrade_api.ssh_password == "test"
        assert remote_freqtrade_api.remote_host == IPvAnyAddress.validate("127.0.0.1")
        assert remote_freqtrade_api.remote_port == 1
        assert remote_freqtrade_api.api_username == "test"
        assert remote_freqtrade_api.api_password == "test"

    def test_RemoteFreqtradeAPI_invalid_port(self):
        with self.assertRaises(ValidationError):
            RemoteFreqtradeAPI(
                ssh_host="127.0.0.1",
                ssh_port="0",
                ssh_username="test",
                ssh_pkey_filename="test",
                ssh_password="test",
                remote_host="127.0.0.1",
                remote_port="1",
                api_username="test",
                api_password="test",
            )
        with self.assertRaises(ValidationError):
            RemoteFreqtradeAPI(
                ssh_host="127.0.0.1",
                ssh_port="65536",
                ssh_username="test",
                ssh_pkey_filename="test",
                ssh_password="test",
                remote_host="127.0.0.1",
                remote_port="1",
                api_username="test",
                api_password="test",
            )
        with self.assertRaises(ValidationError):
            RemoteFreqtradeAPI(
                ssh_host="127.0.0.1",
                ssh_port="1",
                ssh_username="test",
                ssh_pkey_filename="test",
                ssh_password="test",
                remote_host="127.0.0.1",
                remote_port="0",
                api_username="test",
                api_password="test",
            )
        with self.assertRaises(ValidationError):
            RemoteFreqtradeAPI(
                ssh_host="127.0.0.1",
                ssh_port="1",
                ssh_username="test",
                ssh_pkey_filename="test",
                ssh_password="test",
                remote_host="127.0.0.1",
                remote_port="65536",
                api_username="test",
                api_password="test",
            )

    def test_RemoteFreqtradeAPI_missing_attributes(self):
        with self.assertRaises(ValidationError):
            RemoteFreqtradeAPI(
                ssh_host="",
                ssh_port="1",
                ssh_username="test",
                ssh_pkey_filename="test",
                ssh_password="test",
                remote_host="127.0.0.1",
                remote_port="1",
                api_username="test",
                api_password="test",
            )
        with self.assertRaises(ValidationError):
            RemoteFreqtradeAPI(
                ssh_host="127.0.0.1",
                ssh_port="",
                ssh_username="test",
                ssh_pkey_filename="test",
                ssh_password="test",
                remote_host="127.0.0.1",
                remote_port="1",
                api_username="test",
                api_password="test",
            )
        with self.assertRaises(ValueError):
            RemoteFreqtradeAPI(
                ssh_host="127.0.0.1",
                ssh_port="1",
                ssh_username=None,
                ssh_pkey_filename=None,
                ssh_password="test",
                remote_host="127.0.0.1",
                remote_port="1",
                api_username="test",
                api_password="test",
            )
        with self.assertRaises(ValidationError):
            RemoteFreqtradeAPI(
                ssh_host="127.0.0.1",
                ssh_port="1",
                ssh_username="test",
                ssh_pkey_filename="test",
                ssh_password="",
                remote_host="127.0.0.1",
                remote_port="1",
                api_username="test",
                api_password="test",
            )
        with self.assertRaises(ValidationError):
            RemoteFreqtradeAPI(
                ssh_host="127.0.0.1",
                ssh_port="1",
                ssh_username="test",
                ssh_pkey_filename="test",
                ssh_password="test",
                remote_host="",
                remote_port="1",
                api_username="test",
                api_password="test",
            )
        with self.assertRaises(ValidationError):
            RemoteFreqtradeAPI(
                ssh_host="127.0.0.1",
                ssh_port="1",
                ssh_username="test",
                ssh_pkey_filename="test",
                ssh_password="test",
                remote_host="127.0.0.1",
                remote_port="",
                api_username="test",
                api_password="test",
            )
        with self.assertRaises(ValidationError):
            RemoteFreqtradeAPI(
                ssh_host="127.0.0.1",
                ssh_port="1",
                ssh_username="test",
                ssh_pkey_filename="test",
                ssh_password="test",
                remote_host="127.0.0.1",
                remote_port="1",
                api_username="",
                api_password="test",
            )
        with self.assertRaises(ValidationError):
            RemoteFreqtradeAPI(
                ssh_host="127.0.0.1",
                ssh_port="1",
                ssh_username="test",
                ssh_pkey_filename="test",
                ssh_password="test",
                remote_host="127.0.0.1",
                remote_port="1",
                api_username="test",
                api_password="",
            )

    def test_Config_validators(self):
        with self.assertRaises(ValueError):
            Config(
                local_freqtrade_instances=[],
                remote_freqtrade_instances=None,
                scrape_interval=59,
                database_name="freqdash",
            )

        with self.assertRaises(ValueError):
            Config(
                local_freqtrade_instances=None,
                remote_freqtrade_instances=None,
                scrape_interval=60,
                database_name="freqdash",
            )

    @patch("builtins.open")
    @patch("pathlib.Path.is_file")
    def test_load_config(self, mock_is_file, mock_open):
        path = Path("testfile.json")

        mock_is_file.return_value = False
        with self.assertRaises(ValueError) as cm:
            load_config(path)
            assert "testfile.json does not exist" == str(cm.exception)

        mock_is_file.return_value = True
        opener = mock.mock_open(read_data="")
        mock_open.side_effect = opener.side_effect
        mock_open.return_value = opener.return_value
        with self.assertRaises(ValueError) as cm:
            load_config(path)
            assert "ERROR: Invalid JSON: Expecting value, line 1, column 1" == str(
                cm.exception
            )

        opener = mock.mock_open(read_data='{"scrape_interval":0}')
        mock_open.side_effect = opener.side_effect
        mock_open.return_value = opener.return_value
        with self.assertRaises(ValueError) as cm:
            load_config(path)
            assert "ValueError: 2 validation errors for Config" == str(cm.exception)


if __name__ == "__main__":
    unittest.main()
