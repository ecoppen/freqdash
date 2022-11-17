import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

import sqlalchemy as db
from sqlalchemy import DECIMAL, Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

log = logging.getLogger(__name__)

Base = declarative_base()


class User(Base):  # type: ignore
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    nickname = Column(String)


class Database:
    def __init__(self, path: Path) -> None:
        self.engine = db.create_engine(
            "sqlite:///" + str(path) + "?check_same_thread=false"
        )
        log.info(f"Database loaded: {path} ")

        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.Base = declarative_base()

        class Hosts(self.Base):  # type: ignore
            __tablename__ = "hosts"

            id = db.Column(db.Integer, primary_key=True)
            host = db.Column(db.String)
            remote_host = db.Column(db.String)
            exchange = db.Column(db.String)
            strategy = db.Column(db.String)
            state = db.Column(db.String)
            stake_currency = db.Column(db.String)
            trading_mode = db.Column(db.String)
            run_mode = db.Column(db.String)
            ft_version = db.Column(db.String)
            strategy_version = db.Column(db.String)
            added = db.Column(db.DateTime, default=datetime.now)
            last_checked = db.Column(
                db.DateTime, default=datetime.now, onupdate=datetime.now
            )

        self.Base.metadata.create_all(self.engine)  # type: ignore
        log.info("database tables loaded")

    def get_table_object(self, table_name: str):
        self.Base.metadata.reflect(bind=self.engine)  # type: ignore
        return self.Base.metadata.tables[table_name]  # type: ignore

    def get_all_hosts(self):
        table_name = "hosts"
        table_object = self.get_table_object(table_name)
        return self.session.query(table_object).all()

    def check_then_add_or_update_host(self, data):
        table_object = self.get_table_object(table_name="hosts")
        check = (
            self.session.query(table_object)
            .filter_by(host=data["host"], remote_host=data["remote_host"])
            .all()
        )
        if len(check) == 0:
            log.info(
                f"Adding host/remote host to db. Host: {data['host']} Remote host: {data['remote_host']}"
            )
            result = self.engine.execute(table_object.insert().values(data))
            log.info(
                f"Host saved. Host: {data['host']} Remote host: {data['remote_host']}"
            )
            return result
        else:
            log.info(
                f"Updating host in db. Host: {data['host']} Remote host: {data['remote_host']}"
            )
            self.session.query(table_object).filter_by(
                host=data["host"], remote_host=data["remote_host"]
            ).update(data)
            self.session.commit()
            self.session.flush()
            log.info(
                f"Host updated. Host: {data['host']} Remote host: {data['remote_host']}"
            )
        return check

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
        result = self.session.query(func.sum(table_object.c.close_profit_abs)).scalar()
        if result is None:
            return 0.0
        else:
            return result

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
        result = (
            self.session.query(func.sum(table_object.c.close_profit_abs))
            .filter(*filters)
            .scalar()
        )
        if result is None:
            return 0.0
        else:
            return result
