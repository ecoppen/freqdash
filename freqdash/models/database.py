import logging
from pathlib import Path

import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

log = logging.getLogger(__name__)


class Database:
    def __init__(self, path: Path) -> None:
        self.engine = db.create_engine(
            "sqlite:///" + str(path) + "?check_same_thread=false"
        )
        log.info(f"{path.name} loaded")

        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.Base = declarative_base()

    def get_table_object(self, table_name: str):
        self.Base.metadata.reflect(self.engine)  # type: ignore
        return self.Base.metadata.tables.get(table_name)  # type: ignore

    def get_open_trades(self):
        table_name = "trades"
        table_object = self.get_table_object(table_name)

        return self.session.query(table_object).filter_by(is_open=1).all()
