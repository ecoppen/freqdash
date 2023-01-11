import logging
from datetime import datetime
from typing import Optional

import sqlalchemy as db
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

log = logging.getLogger(__name__)

Base = declarative_base()


class Database:
    def __init__(self, config) -> None:
        if config.engine == "postgres":
            engine_string = f"{config.username}:{config.password}@{config.host}:{config.port}/{config.name}"
            self.engine = create_engine("postgresql+psycopg://" + engine_string)
        elif config.engine == "sqlite":
            self.engine = create_engine(
                "sqlite:///" + config.name + ".db?check_same_thread=false"
            )
        else:
            raise Exception(f"{config.engine} setup has not been defined")

        log.info(f"{config.engine} loaded")

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
            starting_capital = db.Column(db.Numeric, nullable=True)
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
            last_process_ts = db.Column(db.Numeric, nullable=True)
            added = db.Column(db.DateTime, default=datetime.now)

        class balances(self.Base):  # type: ignore
            __tablename__ = "balances"

            host_id = db.Column(db.Integer, primary_key=True)
            currency = db.Column(db.String, primary_key=True)
            free = db.Column(db.Numeric)
            balance = db.Column(db.Numeric)

        class base_lists(self.Base):  # type: ignore
            __tablename__ = "base_lists"

            host_id = db.Column(db.Integer, primary_key=True)
            quote = db.Column(db.String, primary_key=True)
            list_type = db.Column(db.Integer, primary_key=True)

        class logs(self.Base):  # type: ignore
            __tablename__ = "logs"

            id = db.Column(db.Integer, primary_key=True)
            host_id = db.Column(db.Integer)
            timestamp = db.Column(db.Integer)
            name = db.Column(db.String)
            level = db.Column(db.String)
            message = db.Column(db.String)

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
                difference = now - host[13]
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
                    "last_checked": host[13].strftime("%Y-%m-%d %H:%M:%S"),
                    "alert": difference.total_seconds() > 600,
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
                        host_id=host[0], is_open=False, limit=10, sort=True
                    )
                    hosts["recent"] += [list(trade) for trade in closed_trades]
                    open_trades = self.get_trades(
                        host_id=host[0], is_open=True, sort=True
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
                log.info(trade)

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

    def get_prices(self, exchange: str, trading_mode: str, quote: str):
        table_object = self.get_table_object(table_name="prices")
        all_prices = (
            self.session.query(table_object)
            .filter_by(exchange=exchange, trading_mode=trading_mode)
            .all()
        )
        prices = []
        for symbol in all_prices:
            if symbol[3].endswith(quote):
                prices.append(symbol)
        return prices

    def delete_then_update_price(self, exchange: str, market: str, data: dict):
        table_object = self.get_table_object(table_name="prices")
        check = (
            self.session.query(table_object)
            .filter_by(exchange=exchange, trading_mode=market)
            .first()
        )

        if check is not None:
            if len(check) > 0:
                log.info(f"Price data found for {exchange}/{market} deleting")
                self.session.query(table_object).filter_by(
                    exchange=exchange, trading_mode=market
                ).delete()
                self.session.commit()
        for item in data:
            item["exchange"] = exchange
            item["trading_mode"] = market
        self.engine.execute(table_object.insert().values(data))
        log.info(f"Price data saved for {exchange}/{market}")

    def get_balances(self, host_id: int):
        table_object = self.get_table_object(table_name="balances")
        balances = self.session.query(table_object).filter_by(host_id=host_id).all()
        return balances

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
        self,
        host_id: int,
        quote_currency: str,
        is_open: bool = True,
        won: bool | None = None,
    ) -> int:
        table_object = self.get_table_object(table_name="trades")
        int_is_open: int = 1 if is_open else 0
        filters = []
        if won is not None:
            if won:
                filters.append(table_object.c.profit_abs >= 0)
            else:
                filters.append(table_object.c.profit_abs < 0)
        filters.append(table_object.c.quote_currency == quote_currency)
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

    def get_orders_for_trade(self, host_id: int, trade_id: int, is_open: bool = False):
        table_object = self.get_table_object(table_name="orders")
        filters = []
        if is_open:
            filters.append(table_object.c.status == "open")
        else:
            filters.append(table_object.c.status == "closed")
        filters.append(table_object.c.host_id == host_id)
        filters.append(table_object.c.trade_id == trade_id)

        return self.session.query(table_object).filter(*filters).all()

    def get_closed_profit(self):
        table_object = self.get_table_object(table_name="trades")
        result = self.session.query(func.sum(table_object.c.profit_abs)).scalar()
        if result is None:
            return 0.0
        else:
            return result

    def get_profit_factor(
        self, host_id: int, quote_currency: str, is_open: bool = False
    ) -> float:
        table_object = self.get_table_object(table_name="trades")

        filters = []
        if is_open:
            filters.append(table_object.c.is_open == 1)
        else:
            filters.append(table_object.c.is_open == 0)

        filters.append(table_object.c.host_id == host_id)
        filters.append(table_object.c.quote_currency == quote_currency)
        filters.append(table_object.c.profit_abs >= 0)

        total_profit = (
            self.session.query(func.sum(table_object.c.profit_abs))
            .filter(*filters)
            .scalar()
        )
        del filters[-1]
        filters.append(table_object.c.profit_abs < 0)
        total_loss = (
            self.session.query(func.sum(table_object.c.profit_abs))
            .filter(*filters)
            .scalar()
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
        result = (
            self.session.query(func.sum(table_object.c.profit_abs))
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

    def add_last_process_ts(self, data: int, host_id: int):
        table_object = self.get_table_object(table_name="sysinfo")
        result = (
            self.session.query(table_object)
            .filter_by(host_id=host_id)
            .order_by(table_object.c.id.desc())
            .first()
        )
        if result is not None:
            self.session.query(table_object).filter_by(
                host_id=host_id, id=result[0]
            ).update({"last_process_ts": data})

            self.session.commit()

    def delete_then_add_baselist(
        self, data: list, host_id: int, list_type: str = "white"
    ):
        table_object = self.get_table_object(table_name="base_lists")

        check = (
            self.session.query(table_object)
            .filter_by(host_id=host_id, list_type=list_type)
            .first()
        )

        if check is not None:
            if len(check) > 0:
                log.info(f"{list_type}list data found for host {host_id} - deleting")
                self.session.query(table_object).filter_by(
                    host_id=host_id, list_type=list_type
                ).delete()
                self.session.commit()

        formatted_data: list = []
        log.info(data)
        for item in data:
            quote = item.split("/")[0]
            formatted_data.append(
                {"host_id": host_id, "quote": quote, "list_type": list_type}
            )
        if len(formatted_data) > 0:
            self.engine.execute(table_object.insert().values(formatted_data))
            log.info(f"{list_type}list data updated for host {host_id}")

    def update_starting_capital(self, data: float, host_id: int):
        table_object = self.get_table_object(table_name="hosts")
        self.session.query(table_object).filter_by(id=host_id).update(
            {"starting_capital": data}
        )
        self.session.commit()

    def update_balances(self, data: list, host_id: int):
        table_object = self.get_table_object(table_name="balances")
        table_keys = table_object.columns.keys()
        check = self.session.query(table_object).filter_by(host_id=host_id).first()

        if check is not None:
            if len(check) > 0:
                log.info(f"balances found for host {host_id} - deleting")
                self.session.query(table_object).filter_by(host_id=host_id).delete()
                self.session.commit()
        for balance in data:
            adjusted_balance = {}
            balance["host_id"] = host_id
            for key in table_keys:
                adjusted_balance[key] = balance[key]
            self.engine.execute(table_object.insert().values(adjusted_balance))

    def update_logs(self, data: list, host_id: int):
        table_object = self.get_table_object(table_name="logs")

        result = (
            self.session.query(table_object)
            .filter_by(host_id=host_id)
            .order_by(table_object.c.id.desc())
            .first()
        )

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
            self.engine.execute(table_object.insert().values(logs))

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
                self.session.commit()
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
