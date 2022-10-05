import logging
from decimal import Decimal
from pathlib import Path
from typing import Optional

import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

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
        self.Base.metadata.reflect(bind=self.engine)  # type: ignore
        return self.Base.metadata.tables[table_name]  # type: ignore

    def get_open_trades(self):
        table_name = "trades"
        table_object = self.get_table_object(table_name)

        return self.session.query(table_object).filter_by(is_open=1).all()

    def get_closed_orders_for_trade(self, trade_id):
        table_name = "orders"
        table_object = self.get_table_object(table_name)

        return (
            self.session.query(table_object)
            .filter_by(ft_trade_id=trade_id, status="closed")
            .all()
        )

    def get_closed_profit(self):
        table_name = "trades"
        table_object = self.get_table_object(table_name)
        return self.session.query(func.sum(table_object.c.close_profit_abs)).scalar()

    def get_closed_profit_between_dates(
        self, start_datetime: Optional[str], end_datetime: Optional[str]
    ):
        table_name = "trades"
        table_object = self.get_table_object(table_name)

        filters = []
        if start_datetime is not None:
            filters.append(table_object.c.close_date >= start_datetime)
        if end_datetime is not None:
            filters.append(table_object.c.close_date <= end_datetime)
        return (
            self.session.query(func.sum(table_object.c.close_profit_abs))
            .filter(*filters)
            .scalar()
        )
