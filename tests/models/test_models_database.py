import unittest
from pathlib import Path

from freqdash.models.database import Database


class TestDatabase(unittest.TestCase):
    def test_database(self):
        path = Path(":memory:")
        database = Database(path=path)

        assert database.get_hosts_and_modes() == {}
        assert database.get_all_hosts() == {
            "live": {},
            "dry": {},
            "recent": [],
            "open": [],
        }


if __name__ == "__main__":
    unittest.main()
