import unittest

from pydantic import IPvAnyAddress

from freqdash.core.config import Database as DBConfig
from freqdash.models.database import Database


class TestDatabase(unittest.TestCase):
    def test_database(self):
        db = DBConfig(
            engine="sqlite",
            username="",
            password="",
            host="127.0.0.1",
            port=5432,
            name="",
        )
        database = Database(config=db)

        assert database.get_hosts_and_modes() == {}
        assert database.get_all_hosts() == {
            "live": {},
            "dry": {},
            "recent": [],
            "open": [],
        }


if __name__ == "__main__":
    unittest.main()
