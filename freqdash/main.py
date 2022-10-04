import logging
import os
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Union

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from freqdash.exchange.factory import load_exchanges
from freqdash.exchange.utils import Exchanges, Intervals, Markets
from freqdash.models.factory import load_databases

logs_file = Path(Path().resolve(), "log.txt")
logs_file.touch(exist_ok=True)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=os.environ.get("LOGLEVEL", "INFO"),
    handlers=[logging.FileHandler(logs_file), logging.StreamHandler()],
)

log = logging.getLogger(__name__)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

exchanges = load_exchanges()
databases = load_databases()


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    data: dict = {"page": "index", "databases": {}}

    for database in databases:
        if database not in data["databases"]:
            data["databases"][database] = {
                "open_trades": [],
                "open_orders": [],
                "profit": {
                    "today": Decimal(0.0),
                    "seven_days": Decimal(0.0),
                    "thirty_days": Decimal(0.0),
                    "realised": Decimal(0.0),
                    "unrealised": Decimal(0.0),
                },
                "realised_daily_profit": [],
                "realised_symbol_profit": {},
            }
        trades = databases[database].get_open_trades()
        for trade in trades:
            id = trade[0]
            exchange = trade[1]
            market = trade[38]
            base = trade[3]
            quote = trade[4]
            open_rate = Decimal(trade[12])
            open_date = trade[22]
            amount = Decimal(trade[20])
            open_date_timedelta = datetime.now() - open_date
            if market == Markets.SPOT:
                url = (
                    exchanges[exchange]
                    .get_spot_trade_url()
                    .replace("BASE", base)
                    .replace("QUOTE", quote)
                )
            else:
                url = (
                    exchanges[exchange]
                    .get_futures_trade_url()
                    .replace("BASE", base)
                    .replace("QUOTE", quote)
                )

            all_closed_orders = databases[database].get_closed_orders_for_trade(
                trade_id=id
            )
            closed_orders = []
            first_order_price = -1
            counter = 1
            for order in all_closed_orders:
                order_id = order[5]
                order_side = order[2]
                order_price = order[10]
                order_amount = order[13]
                order_filled_date = order[19]
                order_filled_timedelta = datetime.now() - order_filled_date
                if first_order_price == -1:
                    first_order_price = order_price
                    difference = Decimal(0.0)
                else:
                    difference = Decimal(
                        f"{(order_price - first_order_price) / first_order_price * 100:.2f}"
                    )
                closed_orders.append(
                    {
                        "counter": counter,
                        "id": order_id,
                        "side": order_side,
                        "price": order_price,
                        "difference": difference,
                        "amount": order_amount,
                        "open_timings": [
                            order_filled_date.strftime("%Y-%m-%d %H:%M:%S"),
                            order_filled_timedelta.days,
                            order_filled_timedelta.seconds // 3600,
                            (order_filled_timedelta.seconds // 60) % 60,
                        ],
                    }
                )
                counter += 1

            current_price = Decimal(
                get_price(exchange=exchange, market=market, base=base, quote=quote)
            )
            current_percentage = Decimal(
                f"{(current_price - open_rate) / open_rate * 100:.2f}"
            )
            data["databases"][database]["open_trades"].append(
                {
                    "open_timings": [
                        open_date.strftime("%Y-%m-%d %H:%M:%S"),
                        open_date_timedelta.days,
                        open_date_timedelta.seconds // 3600,
                        (open_date_timedelta.seconds // 60) % 60,
                    ],
                    "exchange": exchange,
                    "market": market,
                    "symbol": f"{base}{quote}",
                    "open_rate": f"{open_rate:.6f}".rstrip("0"),
                    "amount": f"{amount:.6f}".rstrip("0"),
                    "current_price": f"{current_price:.6f}".rstrip("0"),
                    "current_percentage": current_percentage,
                    "url": url,
                    "orders": closed_orders,
                }
            )
            data["databases"][database]["profit"]["unrealised"] += (
                current_price * amount
            ) - (open_rate * amount)

    return templates.TemplateResponse("index.html", {"request": request, "data": data})


@app.get("/getprices")
def get_prices(
    exchange: Exchanges,
    market: Markets,
):
    if market == Markets.SPOT.value:
        return exchanges[exchange].get_spot_prices()
    else:
        return {"error": "not implemented yet"}


@app.get("/getprice")
def get_price(
    exchange: Exchanges,
    market: Markets,
    base: str,
    quote: str,
):
    if market == Markets.SPOT.value:
        return exchanges[exchange].get_spot_price(
            base=base.upper(), quote=quote.upper()
        )
    else:
        return {"error": "not implemented yet"}


@app.get("/getkline")
def get_kline(
    exchange: Exchanges,
    market: Markets,
    base: str,
    quote: str,
    interval: Intervals = Intervals.ONE_DAY,
    start_time: Union[int, None] = None,
    end_time: Union[int, None] = None,
    limit: int = 500,
):
    if market == Markets.SPOT.value:
        return exchanges[exchange].get_spot_kline(
            base=base.upper(),
            quote=quote.upper(),
            interval=interval,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
        )
    else:
        return {"error": "not implemented yet"}
