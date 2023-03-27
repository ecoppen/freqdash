from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import BigInteger, create_engine, delete, insert, select, update
from sqlalchemy.orm import (  # type: ignore
    DeclarativeBase,
    Mapped,
    MappedAsDataclass,
    Session,
    mapped_column,
)
from sqlalchemy.sql import func
from typing_extensions import Annotated

log = logging.getLogger(__name__)


class Base(MappedAsDataclass, DeclarativeBase):
    pass


intpk = Annotated[int, mapped_column(primary_key=True)]
strpk = Annotated[str, mapped_column(primary_key=True)]


class Database:
    def __init__(self, config) -> None:
        if config.engine == "postgres":
            engine_string = f"{config.username}:{config.password}@{config.host}:{config.port}/{config.name}"
            self.engine = create_engine("postgresql+psycopg://" + engine_string)
        elif config.engine == "sqlite":
            if config.name == "":
                self.engine = create_engine("sqlite:///:memory:")
            else:
                self.engine = create_engine(
                    "sqlite:///" + config.name + ".db?check_same_thread=false"
                )
        else:
            raise Exception(f"{config.engine} setup has not been defined")

        log.info(f"{config.engine} loaded")

        self.Base = Base

        class Hosts(self.Base):  # type: ignore
            __tablename__ = "hosts"

            id: Mapped[intpk] = mapped_column(init=False)
            host: Mapped[str]
            remote_host: Mapped[str]
            exchange: Mapped[str]
            strategy: Mapped[str]
            state: Mapped[str]
            stake_currency: Mapped[str]
            trading_mode: Mapped[str]
            run_mode: Mapped[str]
            ft_version: Mapped[str]
            strategy_version: Mapped[str]
            starting_capital: Mapped[Optional[float]]
            added: Mapped[int] = mapped_column(
                BigInteger, default=self.timestamp(dt=datetime.now())
            )
            last_checked: Mapped[int] = mapped_column(
                BigInteger,
                default=self.timestamp(dt=datetime.now()),
                onupdate=self.timestamp(dt=datetime.now()),
            )

        class Sysinfo(self.Base):  # type: ignore
            __tablename__ = "sysinfo"

            id: Mapped[intpk] = mapped_column(init=False)
            host_id: Mapped[int]
            cpu_pct: Mapped[str]
            ram_pct: Mapped[float]
            last_process_ts: Mapped[Optional[float]]
            added: Mapped[int] = mapped_column(
                BigInteger, default=self.timestamp(dt=datetime.now())
            )

        class balances(self.Base):  # type: ignore
            __tablename__ = "balances"

            host_id: Mapped[intpk] = mapped_column(init=False)
            currency: Mapped[strpk] = mapped_column(init=False)
            free: Mapped[float]
            balance: Mapped[float]

        class base_lists(self.Base):  # type: ignore
            __tablename__ = "base_lists"

            host_id: Mapped[intpk] = mapped_column(init=False)
            quote: Mapped[strpk] = mapped_column(init=False)
            list_type: Mapped[strpk] = mapped_column(init=False)

        class logs(self.Base):  # type: ignore
            __tablename__ = "logs"

            id: Mapped[intpk] = mapped_column(init=False)
            host_id: Mapped[int]
            timestamp: Mapped[int] = mapped_column(BigInteger)
            name: Mapped[str]
            level: Mapped[str]
            message: Mapped[str]

        class Prices(self.Base):  # type: ignore
            __tablename__ = "prices"

            id: Mapped[intpk] = mapped_column(init=False)
            exchange: Mapped[str]
            trading_mode: Mapped[str]
            symbol: Mapped[str]
            price: Mapped[float]
            updated: Mapped[int] = mapped_column(
                BigInteger, default=self.timestamp(dt=datetime.now())
            )

        class Trades(self.Base):  # type: ignore
            __tablename__ = "trades"

            host_id: Mapped[intpk] = mapped_column(init=False)
            trade_id: Mapped[intpk] = mapped_column(init=False)
            pair: Mapped[str]
            base_currency: Mapped[str]
            quote_currency: Mapped[str]
            exchange: Mapped[str]

            is_open: Mapped[bool]
            amount: Mapped[float]
            stake_amount: Mapped[float]
            profit_abs: Mapped[float]
            enter_tag: Mapped[str]

            fee_open_cost: Mapped[float]
            fee_open_currency: Mapped[str]
            fee_close_cost: Mapped[Optional[float]]
            fee_close_currency: Mapped[Optional[str]]

            open_timestamp: Mapped[int] = mapped_column(BigInteger)
            open_rate: Mapped[float]
            close_timestamp: Mapped[Optional[int]] = mapped_column(BigInteger)
            close_rate: Mapped[Optional[float]]

            exit_reason: Mapped[Optional[str]]
            stop_loss_abs: Mapped[float]
            leverage: Mapped[float]
            is_short: Mapped[bool]
            trading_mode: Mapped[str]
            funding_fees: Mapped[float]

        class Orders(self.Base):  # type: ignore
            __tablename__ = "orders"

            host_id: Mapped[intpk] = mapped_column(init=False)
            order_id: Mapped[strpk] = mapped_column(init=False)
            trade_id: Mapped[intpk] = mapped_column(init=False)

            amount: Mapped[float]
            filled: Mapped[float]
            ft_order_side: Mapped[str]
            order_type: Mapped[str]
            order_timestamp: Mapped[int] = mapped_column(BigInteger)
            order_filled_timestamp: Mapped[int] = mapped_column(BigInteger)
            ft_is_entry: Mapped[Optional[bool]]
            status: Mapped[str]
            average: Mapped[Optional[float]]

        class News(self.Base):  # type: ignore
            __tablename__ = "news"

            id: Mapped[intpk] = mapped_column(init=False)
            exchange: Mapped[str]
            headline: Mapped[str]
            category: Mapped[str]
            hyperlink: Mapped[str]
            news_time: Mapped[int] = mapped_column(BigInteger)
            added: Mapped[int] = mapped_column(
                BigInteger, default=self.timestamp(dt=datetime.now())
            )

        self.Base.metadata.create_all(self.engine)  # type: ignore
        log.info("database tables loaded")

    def timestamp(self, dt) -> int:
        return int(dt.replace(tzinfo=timezone.utc).timestamp() * 1000)

    def get_table_object(self, table_name: str):
        self.Base.metadata.reflect(bind=self.engine)  # type: ignore
        return self.Base.metadata.tables[table_name]  # type: ignore

    def get_hosts_and_modes(self) -> dict:
        table_object = self.get_table_object(table_name="hosts")
        with Session(self.engine) as session:
            result = session.execute(select(table_object)).all()
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
        with Session(self.engine) as session:
            result = session.execute(select(table_object)).all()
        hosts: dict = {"live": {}, "dry": {}, "recent": [], "open": []}
        now = self.timestamp(datetime.now(timezone.utc))
        if result is not None:
            for host in result:
                difference = now - host[13]
                today = datetime.now()
                last_checked = datetime.utcfromtimestamp(host[13] / 1000.0)
                delta = today - last_checked
                hosts[host[8]][host[0]] = {
                    "remote": host[1],
                    "local": host[2],
                    "exchange": host[3],
                    "strategy": host[4],
                    "status": host[5].title(),
                    "stake": host[6],
                    "trading_mode": host[7].upper(),
                    "ft_version": host[9],
                    "strategy_version": host[10],
                    "starting_capital": host[11],
                    "last_checked": delta.seconds // 3600,
                    "alert": difference / 1000 > 600,
                }
                if index:
                    hosts[host[8]][host[0]]["closed_trades"] = self.get_trades_count(
                        host_id=host[0], is_open=False, quote_currency=host[6]
                    )
                    hosts[host[8]][host[0]]["winning_trades"] = self.get_trades_count(
                        host_id=host[0], is_open=False, quote_currency=host[6], won=True
                    )
                    hosts[host[8]][host[0]]["losing_trades"] = (
                        hosts[host[8]][host[0]]["closed_trades"]
                        - hosts[host[8]][host[0]]["winning_trades"]
                    )
                    hosts[host[8]][host[0]]["closed_profit"] = self.get_trade_profit(
                        host_id=host[0], is_open=False, quote_currency=host[6]
                    )
                    if hosts[host[8]][host[0]]["starting_capital"] > 0:
                        hosts[host[8]][host[0]]["total_profit_percentage"] = round(
                            hosts[host[8]][host[0]]["closed_profit"]
                            / hosts[host[8]][host[0]]["starting_capital"]
                            * 100,
                            2,
                        )
                    else:
                        hosts[host[8]][host[0]]["total_profit_percentage"] = 0

                    first_trade = self.get_trades(
                        host_id=host[0], is_open=False, limit=1, sort=True, order="asc"
                    )
                    if len(first_trade) > 0:
                        first_trade_date = datetime.utcfromtimestamp(
                            first_trade[0][15] / 1000.0
                        )
                        delta = today - first_trade_date
                        hosts[host[8]][host[0]]["days_from_first_trade"] = delta.days
                    else:
                        hosts[host[8]][host[0]]["days_from_first_trade"] = 0

                    if hosts[host[8]][host[0]]["days_from_first_trade"] > 0:
                        hosts[host[8]][host[0]]["daily_profit_percentage"] = round(
                            hosts[host[8]][host[0]]["total_profit_percentage"]
                            / hosts[host[8]][host[0]]["days_from_first_trade"],
                            2,
                        )
                    else:
                        hosts[host[8]][host[0]]["daily_profit_percentage"] = 0

                    hosts[host[8]][host[0]]["open_trades"] = self.get_trades_count(
                        host_id=host[0], is_open=True, quote_currency=host[6]
                    )
                    hosts[host[8]][host[0]]["open_profit"] = self.get_trade_profit(
                        host_id=host[0], is_open=True, quote_currency=host[6]
                    )

                    hosts[host[8]][host[0]]["profit_factor"] = self.get_profit_factor(
                        host_id=host[0], is_open=False, quote_currency=host[6]
                    )

                    closed_trades = self.get_trades(
                        host_id=host[0],
                        is_open=False,
                        limit=10,
                        sort=True,
                        order="desc",
                    )
                    hosts["recent"] += [list(trade) for trade in closed_trades]
                    open_trades = self.get_trades(
                        host_id=host[0], is_open=True, sort=True, order="desc"
                    )
                    hosts["open"] += [list(trade) for trade in open_trades]

            hosts["recent"].sort(key=lambda x: x[17], reverse=True)
            hosts["recent"] = hosts["recent"][:10]
            for trade in hosts["recent"]:
                trade[17] = datetime.utcfromtimestamp(trade[17] / 1000.0).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                trade[15] = datetime.utcfromtimestamp(trade[15] / 1000.0).strftime(
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

                orders = self.get_orders_for_trade(
                    host_id=trade[0], trade_id=trade[1], is_open=False
                )
                buy, sell = 0, 0
                for order in orders:
                    if order[5] == "buy":
                        buy += 1
                    else:
                        sell += 1
                trade += [buy, sell]

        return hosts

    def check_then_add_or_update_host(self, data):
        table_object = self.get_table_object(table_name="hosts")
        with Session(self.engine) as session:
            check = session.scalars(
                select(table_object)
                .filter_by(host=data["host"], remote_host=data["remote_host"])
                .limit(1)
            ).first()
            if check is None:
                log.info(
                    f"Adding host/remote host to db. Host: {data['host']} Remote host: {data['remote_host']}"
                )
                session.execute(insert(table_object), data)
                log.info(
                    f"Host saved. Host: {data['host']} Remote host: {data['remote_host']}"
                )
                check = session.scalars(
                    select(table_object)
                    .filter_by(host=data["host"], remote_host=data["remote_host"])
                    .limit(1)
                ).first()
            else:
                log.info(
                    f"Updating host in db. Host: {data['host']} Remote host: {data['remote_host']}"
                )
                filters = []
                filters.append(table_object.c.host == data["host"])
                filters.append(table_object.c.remote_host == data["remote_host"])
                session.execute(update(table_object).where(*filters).values(data))
                log.info(
                    f"Host updated. Host: {data['host']} Remote host: {data['remote_host']}"
                )
            session.commit()
        return check

    def get_current_price(self, exchange: str, symbol: str, trading_mode: str):
        table_object = self.get_table_object(table_name="prices")
        with Session(self.engine) as session:
            price = session.execute(
                select(table_object)
                .filter_by(exchange=exchange, trading_mode=trading_mode, symbol=symbol)
                .limit(1)
            ).first()
        return price

    def get_prices(self, exchange: str, trading_mode: str, quote: str) -> dict:
        table_object = self.get_table_object(table_name="prices")
        with Session(self.engine) as session:
            all_prices = session.execute(
                select(table_object).filter_by(
                    exchange=exchange, trading_mode=trading_mode
                )
            ).all()
        prices = {}
        for symbol in all_prices:
            if symbol[3].endswith(quote) or symbol[3].startswith(quote):
                prices[symbol[3]] = symbol[4]
        return prices

    def delete_then_update_price(self, exchange: str, market: str, data: dict):
        table_object = self.get_table_object(table_name="prices")

        with Session(self.engine) as session:
            check = session.scalars(
                select(table_object)
                .filter_by(exchange=exchange, trading_mode=market)
                .limit(1)
            ).first()

            if check is not None:
                if check > 0:
                    log.info(f"Price data found for {exchange}/{market} deleting")
                    filters = []
                    filters.append(table_object.c.exchange == exchange)
                    filters.append(table_object.c.trading_mode == market)
                    session.execute(delete(table_object).where(*filters))
            for item in data:
                item["exchange"] = exchange
                item["trading_mode"] = market
            session.execute(insert(table_object), data)
            session.commit()
        log.info(f"Price data saved for {exchange}/{market}")

    def get_balances(self, host_id: int):
        table_object = self.get_table_object(table_name="balances")
        with Session(self.engine) as session:
            balances = session.execute(
                select(table_object).filter_by(host_id=host_id)
            ).all()
        return balances

    def get_trades(
        self,
        host_id: int,
        is_open: bool = True,
        limit: int | None = None,
        sort: bool = False,
        order: str = "",
    ):
        table_object = self.get_table_object(table_name="trades")
        with Session(self.engine) as session:
            if sort:
                if order == "asc":
                    trades = session.execute(
                        select(table_object)
                        .filter_by(host_id=host_id, is_open=is_open)
                        .order_by(table_object.c.close_timestamp.asc())
                    ).all()
                else:
                    trades = session.execute(
                        select(table_object)
                        .filter_by(host_id=host_id, is_open=is_open)
                        .order_by(table_object.c.close_timestamp.desc())
                    ).all()
            else:
                trades = session.execute(
                    select(table_object).filter_by(host_id=host_id, is_open=is_open)
                ).all()
        if limit is not None:
            return trades[:limit]
        return trades

    def get_trades_count(
        self,
        host_id: int,
        quote_currency: str,
        is_open: bool = True,
        won: bool | None = None,
    ) -> int:
        table_object = self.get_table_object(table_name="trades")
        filters = []
        if won is not None:
            if won:
                filters.append(table_object.c.profit_abs >= 0)
            else:
                filters.append(table_object.c.profit_abs < 0)
        filters.append(table_object.c.quote_currency == quote_currency)
        filters.append(table_object.c.host_id == host_id)
        filters.append(table_object.c.is_open == is_open)
        with Session(self.engine) as session:
            count = session.scalar(
                select(func.count()).select_from(table_object).filter(*filters)
            )
        if count is None:
            return 0
        return count

    def get_trade_profit(self, host_id: int, quote_currency: str, is_open: bool = True):
        table_object = self.get_table_object(table_name="trades")
        filters = []
        filters.append(table_object.c.is_open == is_open)
        filters.append(table_object.c.host_id == host_id)
        filters.append(table_object.c.quote_currency == quote_currency)
        with Session(self.engine) as session:
            result = session.scalar(
                select(func.sum(table_object.c.profit_abs))
                .select_from(table_object)
                .filter(*filters)
            )
        if result is None:
            return 0.0
        else:
            return round(result, 2)

    def get_orders_for_trade(self, host_id: int, trade_id: int, is_open: bool = False):
        table_object = self.get_table_object(table_name="orders")
        filters = []
        if is_open:
            filters.append(table_object.c.status == "open")
        else:
            filters.append(table_object.c.status == "closed")
        filters.append(table_object.c.host_id == host_id)
        filters.append(table_object.c.trade_id == trade_id)
        with Session(self.engine) as session:
            orders = session.execute(select(table_object).filter(*filters)).all()
        return orders

    def get_closed_profit(self):
        table_object = self.get_table_object(table_name="trades")
        with Session(self.engine) as session:
            result = session.scalar(
                select(func.sum(table_object.c.profit_abs))
                .select_from(table_object)
                .filter()
            )
        if result is None:
            return 0.0
        else:
            return result

    def get_profit_factor(
        self, host_id: int, quote_currency: str, is_open: bool = False
    ) -> float:
        table_object = self.get_table_object(table_name="trades")

        filters = []
        filters.append(table_object.c.is_open == is_open)
        filters.append(table_object.c.host_id == host_id)
        filters.append(table_object.c.quote_currency == quote_currency)
        filters.append(table_object.c.profit_abs >= 0)

        with Session(self.engine) as session:
            total_profit = session.scalar(
                select(func.sum(table_object.c.profit_abs))
                .select_from(table_object)
                .filter(*filters)
            )
            del filters[-1]
            filters.append(table_object.c.profit_abs < 0)
            total_loss = session.scalar(
                select(func.sum(table_object.c.profit_abs))
                .select_from(table_object)
                .filter(*filters)
            )
        if total_profit is None:
            return 0.0
        if total_loss is None:
            return float("inf")
        return round(total_profit / abs(total_loss), 2)

    def get_closed_profit_between_dates(
        self, start_datetime: Optional[str], end_datetime: Optional[str]
    ):
        table_object = self.get_table_object(table_name="trades")

        filters = []
        if start_datetime is not None:
            filters.append(table_object.c.close_date >= start_datetime)
        if end_datetime is not None:
            filters.append(table_object.c.close_date <= end_datetime)
        with Session(self.engine) as session:
            result = session.scalar(
                select(func.sum(table_object.c.profit_abs))
                .select_from(table_object)
                .filter(*filters)
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

        with Session(self.engine) as session:
            session.execute(insert(table_object), data)
            session.commit()

    def add_last_process_ts(self, data: int, host_id: int):
        table_object = self.get_table_object(table_name="sysinfo")
        with Session(self.engine) as session:
            result = session.scalars(
                select(table_object)
                .filter_by(host_id=host_id)
                .order_by(table_object.c.id.desc())
                .limit(1)
            ).first()
            if result is not None:
                filters = []
                filters.append(table_object.c.host_id == host_id)
                filters.append(table_object.c.id == result)
                session.execute(
                    update(table_object)
                    .where(*filters)
                    .values({"last_process_ts": data})
                )
                session.commit()

    def delete_then_add_baselist(
        self, data: list, host_id: int, list_type: str = "white"
    ):
        table_object = self.get_table_object(table_name="base_lists")
        with Session(self.engine) as session:
            check = session.scalars(
                select(table_object)
                .filter_by(host_id=host_id, list_type=list_type)
                .limit(1)
            ).first()

            if check is not None:
                if check > 0:
                    log.info(
                        f"{list_type}list data found for host {host_id} - deleting"
                    )
                    filters = []
                    filters.append(table_object.c.host_id == host_id)
                    filters.append(table_object.c.list_type == list_type)
                    session.execute(delete(table_object).where(*filters))

            formatted_data: list = []
            for item in data:
                quote = item.split("/")[0]
                formatted_data.append(
                    {"host_id": host_id, "quote": quote, "list_type": list_type}
                )
            if len(formatted_data) > 0:
                session.execute(insert(table_object), formatted_data)
                log.info(f"{list_type}list data updated for host {host_id}")
            session.commit()

    def update_starting_capital(self, data: float, host_id: int):
        table_object = self.get_table_object(table_name="hosts")
        with Session(self.engine) as session:
            filters = []
            filters.append(table_object.c.id == host_id)
            session.execute(
                update(table_object).where(*filters).values({"starting_capital": data})
            )
            session.commit()

    def update_balances(self, data: list, host_id: int):
        table_object = self.get_table_object(table_name="balances")
        table_keys = table_object.columns.keys()
        with Session(self.engine) as session:
            check = session.scalars(
                select(table_object).filter_by(host_id=host_id).limit(1)
            ).first()

            if check is not None:
                if check > 0:
                    log.info(f"balances found for host {host_id} - deleting")
                    filters = []
                    filters.append(table_object.c.host_id == host_id)
                    session.execute(delete(table_object).where(*filters))

            for balance in data:
                adjusted_balance = {}
                balance["host_id"] = host_id
                for key in table_keys:
                    adjusted_balance[key] = balance[key]
                session.execute(insert(table_object), adjusted_balance)
            log.info(f"Updating balances for host {host_id}")
            session.commit()

    def update_logs(self, data: list, host_id: int):
        table_object = self.get_table_object(table_name="logs")

        with Session(self.engine) as session:
            result = session.execute(
                select(table_object)
                .filter_by(host_id=host_id)
                .order_by(table_object.c.id.desc())
                .limit(1)
            ).first()

        timestamp = 0
        if result is not None:
            if len(result) > 0:
                timestamp = result[2]

        logs = []
        for log_item in data:
            ts = int(log_item[1])
            if ts > timestamp:
                log_data = {
                    "host_id": host_id,
                    "timestamp": ts,
                    "name": log_item[2],
                    "level": log_item[3],
                    "message": log_item[4],
                }
                logs.append(log_data)

        if len(logs) > 0:
            with Session(self.engine) as session:
                session.execute(insert(table_object), logs)
                session.commit()

    def get_oldest_open_trade_id(self, host_id: int):
        table_object = self.get_table_object(table_name="trades")
        with Session(self.engine) as session:
            result = session.execute(
                select(table_object)
                .filter_by(host_id=host_id, is_open=True)
                .order_by(table_object.c.trade_id.asc())
                .limit(1)
            ).first()
        if result is None:
            with Session(self.engine) as session:
                result = session.execute(
                    select(table_object)
                    .filter_by(host_id=host_id, is_open=True)
                    .order_by(table_object.c.trade_id.asc())
                    .limit(1)
                ).first()
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
            with Session(self.engine) as session:
                check = session.execute(
                    select(table_object)
                    .filter_by(host_id=host_id, trade_id=trade["trade_id"])
                    .limit(1)
                ).first()
            adjusted_trade = {}
            for key in table_keys:
                adjusted_trade[key] = trade[key]
            if check is None:
                log.info(
                    f"Adding trade to db. Host: {host_id} Trade: {trade['trade_id']} - {trade['pair']}"
                )
                with Session(self.engine) as session:
                    session.execute(insert(table_object), adjusted_trade)
                    session.commit()
            else:
                log.info(f"Trade {trade['trade_id']} already in DB, updating")
                with Session(self.engine) as session:
                    filters = []
                    filters.append(table_object.c.host_id == host_id)
                    filters.append(table_object.c.trade_id == trade["trade_id"])
                    session.execute(
                        update(table_object).where(*filters).values(adjusted_trade)
                    )
                    session.commit()

            self.check_then_update_or_add_orders(
                data=trade["orders"], host_id=host_id, trade_id=trade["trade_id"]
            )

    def check_then_update_or_add_orders(self, data: dict, host_id: int, trade_id: int):
        table_object = self.get_table_object(table_name="orders")
        table_keys = table_object.columns.keys()
        for order in data:
            order = order | {"host_id": host_id, "trade_id": trade_id}
            with Session(self.engine) as session:
                check = session.execute(
                    select(table_object)
                    .filter_by(
                        host_id=host_id, trade_id=trade_id, order_id=order["order_id"]
                    )
                    .limit(1)
                ).first()
            adjusted_order = {}
            for key in table_keys:
                if key in order:
                    adjusted_order[key] = order[key]

            if check is None:
                log.info(
                    f"Adding order to db. Host: {host_id} Trade: {trade_id} Order:{order['order_id']}"
                )
                with Session(self.engine) as session:
                    session.execute(insert(table_object), adjusted_order)
                    session.commit()
            else:
                log.info(f"Order {order['order_id']} already in DB, updating")
                with Session(self.engine) as session:
                    filters = []
                    filters.append(table_object.c.host_id == host_id)
                    filters.append(table_object.c.trade_id == trade_id)
                    filters.append(table_object.c.order_id == order["order_id"])
                    session.execute(
                        update(table_object).where(*filters).values(adjusted_order)
                    )
                    session.commit()

    def get_instance(self, instance_id: int) -> dict:
        table_object = self.get_table_object(table_name="hosts")
        instance_data: dict = {}
        with Session(self.engine) as session:
            account = session.execute(
                select(table_object).filter_by(id=instance_id)
            ).first()
            if account:
                instance_data = {
                    "remote_host": account[1],
                    "exchange": account[2],
                    "strategy": account[3],
                    "state": account[4],
                    "stake_currency": account[5],
                    "trading_mode": account[6],
                    "run_mode": account[7],
                    "ft_version": account[8],
                    "strategy_version": account[9],
                    "starting_capital": account[10],
                    "added": account[11],
                    "last_checked": account[12],
                }
        return instance_data

    def delete_then_update_news(self, exchange: str, data: dict) -> None:
        table_object = self.get_table_object(table_name="news")

        with Session(self.engine) as session:
            check = session.scalars(
                select(table_object).filter_by(exchange=exchange).limit(1)
            ).first()

            if check is not None:
                if check > 0:
                    log.info(f"News data found for account {exchange} - deleting")
                    filters = [table_object.c.exchange == exchange]
                    session.execute(delete(table_object).where(*filters))
            if len(data) > 0:
                for item in data:
                    item["exchange"] = exchange
                session.execute(insert(table_object), data)
            session.commit()
        log.info(f"News data updated for {exchange}: {len(data)}")

    def get_count_news_items(
        self,
        start: int | None = None,
        end: int | None = None,
        exchange: str | None = None,
    ) -> int:
        table_object = self.get_table_object(table_name="news")
        with Session(self.engine) as session:
            filters = []
            if start is not None:
                filters.append(table_object.c.news_time >= start)
            if end is not None:
                filters.append(table_object.c.news_time < end)
            if exchange is not None:
                filters.append(table_object.c.exchange == exchange)
            count = session.scalar(
                select(func.count()).select_from(table_object).filter(*filters)
            )
        if count is not None:
            return count
        return 0

    def get_news_items(
        self, start: int | None, end: int | None, exchange: str | None
    ) -> list:
        table_object = self.get_table_object(table_name="news")
        all_news: list = []
        with Session(self.engine) as session:
            filters = []
            if start is not None:
                filters.append(table_object.c.news_time >= start)
            if end is not None:
                filters.append(table_object.c.news_time < end)
            if exchange is not None:
                filters.append(table_object.c.exchange == exchange)
            news = session.execute(
                select(table_object)
                .filter(*filters)
                .order_by(table_object.c.news_time.desc())
            ).all()
        if news is None:
            return all_news
        if len(news) == 0:
            return all_news
        for news_item in news:
            all_news.append(
                {
                    "exchange": news_item[1],
                    "headline": news_item[2],
                    "category": news_item[3],
                    "hyperlink": news_item[4],
                    "timestamp": news_item[5],
                }
            )
        return all_news
