import unittest
from pathlib import Path

from freqdash.models.database import Database


class TestCoreConfig(unittest.TestCase):
    def test_database(self):
        path = Path(":memory:")
        database = Database(path=path)

        assert database.get_hosts_and_modes() == {}


if __name__ == "__main__":
    unittest.main()
