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

        class Sysinfo(self.Base):  # type: ignore
            __tablename__ = "sysinfo"

            id = db.Column(db.Integer, primary_key=True)
            host_id = db.Column(db.Integer)
            cpu_pct = db.Column(db.Numeric)
            ram_pct = db.Column(db.Numeric)
            added = db.Column(db.DateTime, default=datetime.now)

        class Prices(self.Base):  # type: ignore
            __tablename__ = "prices"

            id = db.Column(db.Integer, primary_key=True)
            exchange = db.Column(db.String)
            trading_mode = db.Column(db.String)
            symbol = db.Column(db.String)
            price = db.Column(db.Numeric)
            updated = db.Column(db.DateTime, default=datetime.now)

        class Trades(self.Base):  # type: ignore
            __tablename__ = "trades"

            host_id = db.Column(db.Integer, primary_key=True)
            trade_id = db.Column(db.Integer, primary_key=True)
            pair = db.Column(db.String)
            base_currency = db.Column(db.String)
            quote_currency = db.Column(db.String)
            exchange = db.Column(db.String)

            is_open = db.Column(db.Boolean)
            amount = db.Column(db.Numeric)
            stake_amount = db.Column(db.Numeric)
            profit_abs = db.Column(db.Numeric)
            enter_tag = db.Column(db.String)

            fee_open_cost = db.Column(db.Numeric)
            fee_open_currency = db.Column(db.String)
            fee_close_cost = db.Column(db.Numeric)
            fee_close_currency = db.Column(db.String)

            open_timestamp = db.Column(db.Integer)
            open_rate = db.Column(db.Numeric)
            close_timestamp = db.Column(db.Integer)
            close_rate = db.Column(db.Numeric)

            exit_reason = db.Column(db.String)
            stop_loss_abs = db.Column(db.Numeric)
            leverage = db.Column(db.Numeric)
            is_short = db.Column(db.Boolean)
            trading_mode = db.Column(db.String)
            funding_fees = db.Column(db.Numeric)

        class Orders(self.Base):  # type: ignore
            __tablename__ = "orders"

            host_id = db.Column(db.Integer, primary_key=True)
            order_id = db.Column(db.Integer, primary_key=True)
            trade_id = db.Column(db.Integer, primary_key=True)

            amount = db.Column(db.Numeric)
            filled = db.Column(db.Numeric)
            ft_order_side = db.Column(db.String)
            order_type = db.Column(db.String)
            order_timestamp = db.Column(db.Integer)
            order_filled_timestamp = db.Column(db.Integer)
            ft_is_entry = db.Column(db.Boolean, nullable=True)
            status = db.Column(db.String)
            average = db.Column(db.Numeric, nullable=True)

        self.Base.metadata.create_all(self.engine)  # type: ignore
        log.info("database tables loaded")

    def get_table_object(self, table_name: str):
        self.Base.metadata.reflect(bind=self.engine)  # type: ignore
        return self.Base.metadata.tables[table_name]  # type: ignore

    def get_hosts_and_modes(self) -> dict:
        table_object = self.get_table_object(table_name="hosts")
        result = self.session.query(table_object).all()
        hosts: dict = {}
        if result is not None:
            for host in result:
                if host[3] not in hosts:
                    hosts[host[3]] = []
                if host[7] not in hosts[host[3]]:
                    hosts[host[3]].append(host[7])
        return hosts

    def get_all_hosts(self, index: bool = False) -> dict:
        table_object = self.get_table_object(table_name="hosts")
        result = self.session.query(table_object).all()
        hosts: dict = {"live": {}, "dry": {}, "recent": [], "open": []}
        now = datetime.now()
        if result is not None:
            for host in result:
                difference = now - host[12]
                hosts[host[8]][host[0]] = {
                    "remote": host[1],
                    "local": host[2],
                    "exchange": host[3],
                    "strategy": host[4],
                    "status": host[5],
                    "stake": host[6],
                    "trading_mode": host[7].upper(),
                    "ft_version": host[9],
                    "strategy_version": host[10],
                    "last_checked": host[12].strftime("%Y-%m-%d %H:%M:%S"),
                    "alert": difference.total_seconds() > 600,
                }
                if index:
                    hosts[host[8]][host[0]]["closed_trades"] = self.get_trades_count(
                        host_id=host[0], is_open=False
                    )
                    hosts[host[8]][host[0]]["winning_trades"] = self.get_trades_count(
                        host_id=host[0], is_open=False, won=True
                    )
                    hosts[host[8]][host[0]]["losing_trades"] = (
                        hosts[host[8]][host[0]]["closed_trades"]
                        - hosts[host[8]][host[0]]["winning_trades"]
                    )
                    hosts[host[8]][host[0]]["closed_profit"] = self.get_trade_profit(
                        host_id=host[0], is_open=False, quote_currency=host[6]
                    )
                    hosts[host[8]][host[0]]["open_trades"] = self.get_trades_count(
                        host_id=host[0], is_open=True
                    )
                    hosts[host[8]][host[0]]["open_profit"] = self.get_trade_profit(
                        host_id=host[0], is_open=True, quote_currency=host[6]
                    )
                    closed_trades = self.get_trades(
                        host_id=host[0], is_open=False, limit=10, sort=True
                    )
                    hosts["recent"] += [list(trade) for trade in closed_trades]
                    open_trades = self.get_trades(
                        host_id=host[0], is_open=True, sort=True
                    )
                    hosts["open"] += [list(trade) for trade in open_trades]

            hosts["recent"].sort(key=lambda x: x[16], reverse=True)
            hosts["recent"] = hosts["recent"][:10]
            for trade in hosts["recent"]:
                trade[17] = datetime.utcfromtimestamp(trade[17] / 1000.0).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            hosts["open"].sort(key=lambda x: x[15])
            for trade in hosts["open"]:
                trade[15] = datetime.utcfromtimestamp(trade[15] / 1000.0).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                current_price = self.get_current_price(
                    symbol=f"{trade[3]}{trade[4]}",
                    exchange=trade[5],
                    trading_mode=trade[23],
                )
                if current_price is not None:
                    trade += [
                        current_price[4],
                        (current_price[4] - trade[16]) / trade[16] * 100,
                    ]
                else:
                    trade += [None, None]

        return hosts

    def check_then_add_or_update_host(self, data):
        table_object = self.get_table_object(table_name="hosts")
        check = (
            self.session.query(table_object)
            .filter_by(host=data["host"], remote_host=data["remote_host"])
            .first()
        )
        if check is None:
            log.info(
                f"Adding host/remote host to db. Host: {data['host']} Remote host: {data['remote_host']}"
            )
            self.engine.execute(table_object.insert().values(data))
            log.info(
                f"Host saved. Host: {data['host']} Remote host: {data['remote_host']}"
            )
            check = (
                self.session.query(table_object)
                .filter_by(host=data["host"], remote_host=data["remote_host"])
                .first()
            )
            return check[0]
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
            check = (
                self.session.query(table_object)
                .filter_by(host=data["host"], remote_host=data["remote_host"])
                .first()
            )
        return check[0]

    def get_current_price(self, exchange: str, symbol: str, trading_mode: str):
        table_object = self.get_table_object(table_name="prices")
        price = (
            self.session.query(table_object)
            .filter_by(exchange=exchange, trading_mode=trading_mode, symbol=symbol)
            .first()
        )
        return price

    def delete_then_update_price(self, exchange: str, market: str, data: dict):
        table_object = self.get_table_object(table_name="prices")
        check = (
            self.session.query(table_object)
            .filter_by(exchange=exchange, trading_mode=market)
            .all()
        )

        if check is not None:
            if len(check) > 0:
                log.info(f"Price data found for {exchange}/{market} deleting")
                self.session.query(table_object).filter_by(
                    exchange=exchange, trading_mode=market
                ).delete()
                self.session.commit()
                self.session.flush()
        for item in data:
            item["exchange"] = exchange
            item["trading_mode"] = market
        self.engine.execute(table_object.insert().values(data))
        log.info(f"Price data saved for {exchange}/{market}")

    def get_trades(
        self,
        host_id: int,
        is_open: bool = True,
        limit: int | None = None,
        sort: bool = False,
    ):
        table_object = self.get_table_object(table_name="trades")
        int_is_open: int = 1 if is_open else 0
        if sort:
            trades = (
                self.session.query(table_object)
                .filter_by(host_id=host_id, is_open=int_is_open)
                .order_by(table_object.c.close_timestamp.desc())
                .all()
            )
        else:
            trades = (
                self.session.query(table_object)
                .filter_by(host_id=host_id, is_open=is_open)
                .all()
            )
        if limit is not None:
            return trades[:limit]
        return trades

    def get_trades_count(
        self, host_id: int, is_open: bool = True, won: bool | None = None
    ) -> int:
        table_object = self.get_table_object(table_name="trades")
        int_is_open: int = 1 if is_open else 0
        filters = []
        if won is not None:
            if won:
                filters.append(table_object.c.profit_abs >= 0)
            else:
                filters.append(table_object.c.profit_abs < 0)
        filters.append(table_object.c.host_id == host_id)
        filters.append(table_object.c.is_open == int_is_open)
        return (
            self.session.query(func.count(table_object.c.trade_id))
            .filter(*filters)
            .scalar()
        )

    def get_trade_profit(self, host_id: int, quote_currency: str, is_open: bool = True):
        table_object = self.get_table_object(table_name="trades")
        filters = []
        if is_open:
            filters.append(table_object.c.is_open == 1)
        else:
            filters.append(table_object.c.is_open == 0)
        filters.append(table_object.c.host_id == host_id)
        filters.append(table_object.c.quote_currency == quote_currency)
        result = (
            self.session.query(func.sum(table_object.c.profit_abs))
            .filter(*filters)
            .scalar()
        )
        if result is None:
            return 0.0
        else:
            return round(result, 2)

    def get_closed_orders_for_trade(self, trade_id):
        table_object = self.get_table_object(table_name="orders")

        return (
            self.session.query(table_object)
            .filter_by(ft_trade_id=trade_id, status="closed")
            .all()
        )

    def get_closed_profit(self):
        table_object = self.get_table_object(table_name="trades")
        result = self.session.query(func.sum(table_object.c.close_profit_abs)).scalar()
        if result is None:
            return 0.0
        else:
            return result

    def get_closed_profit_between_dates(
        self, start_datetime: Optional[str], end_datetime: Optional[str]
    ):
        table_object = self.get_table_object(table_name="trades")

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

    def add_sysinfo(self, data):
        table_object = self.get_table_object(table_name="sysinfo")
        log.info(
            f"Adding sysinfo. Host_id: {data['host_id']} CPU: {data['cpu_pct']} RAM: {data['ram_pct']}"
        )
        self.engine.execute(table_object.insert().values(data))

    def get_oldest_open_trade_id(self, host_id: int):
        table_object = self.get_table_object(table_name="trades")
        result = (
            self.session.query(table_object)
            .filter_by(host_id=host_id, is_open=True)
            .order_by(table_object.c.trade_id.asc())
            .first()
        )
        if result is None:
            result = (
                self.session.query(table_object)
                .filter_by(host_id=host_id)
                .order_by(table_object.c.trade_id.asc())
                .first()
            )
            if result is None:
                return 0
            else:
                return result[1]
        else:
            return result[1]

    def check_then_add_trades(self, data: list, host_id: int):
        table_object = self.get_table_object(table_name="trades")
        table_keys = table_object.columns.keys()
        for trade in data:
            trade = trade | {"host_id": host_id}
            trade["trading_mode"] = trade["trading_mode"].upper()
            check = (
                self.session.query(table_object)
                .filter_by(host_id=host_id, trade_id=trade["trade_id"])
                .first()
            )
            adjusted_trade = {}
            for key in table_keys:
                adjusted_trade[key] = trade[key]
            if check is None:
                log.info(
                    f"Adding trade to db. Host: {host_id} Trade: {trade['trade_id']} - {trade['pair']}"
                )
                self.engine.execute(table_object.insert().values(adjusted_trade))
            else:
                log.info(f"Trade {trade['trade_id']} already in DB, updating")
                self.session.query(table_object).filter_by(
                    host_id=host_id, trade_id=trade["trade_id"]
                ).update(adjusted_trade)

            self.check_then_update_or_add_orders(
                data=trade["orders"], host_id=host_id, trade_id=trade["trade_id"]
            )

    def check_then_update_or_add_orders(self, data: dict, host_id: int, trade_id: int):
        table_object = self.get_table_object(table_name="orders")
        table_keys = table_object.columns.keys()
        for order in data:
            order = order | {"host_id": host_id, "trade_id": trade_id}
            check = (
                self.session.query(table_object)
                .filter_by(
                    host_id=host_id, trade_id=trade_id, order_id=order["order_id"]
                )
                .first()
            )
            adjusted_order = {}
            for key in table_keys:
                if key in order:
                    adjusted_order[key] = order[key]

            if check is None:
                log.info(
                    f"Adding order to db. Host: {host_id} Trade: {trade_id} Order:{order['order_id']}"
                )
                self.engine.execute(table_object.insert().values(adjusted_order))
            else:
                log.info(f"Order {order['order_id']} already in DB, updating")
                self.session.query(table_object).filter_by(
                    host_id=host_id, trade_id=trade_id, order_id=order["order_id"]
                ).update(adjusted_order)

        self.session.commit()
        self.session.flush()
