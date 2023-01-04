import logging
import os
import threading
import time
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from freqdash.connection.factory import load_tunnels
from freqdash.core.config import load_config
from freqdash.exchange.factory import load_exchanges
from freqdash.exchange.utils import Exchanges, Intervals, Markets, Settle
from freqdash.models.database import Database
from freqdash.scraper.scraper import Scraper

logs_file = Path(Path().resolve(), "log.txt")
logs_file.touch(exist_ok=True)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=os.environ.get("LOGLEVEL", "INFO"),
    handlers=[logging.FileHandler(logs_file), logging.StreamHandler()],
)

log = logging.getLogger(__name__)
log.info("freqdash started")

ssh_keys_folder = Path(Path().resolve(), "ssh_keys")
config_file = Path(Path().resolve(), "config", "config.json")
config = load_config(path=config_file)
database_file = Path(Path().resolve(), f"{config.database_name}.db")
database = Database(path=database_file)
tunnels = load_tunnels(
    config=config.remote_freqtrade_instances, ssh_keys_folder=ssh_keys_folder
)
scraper = Scraper(tunnels=tunnels, database=database)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(GZipMiddleware)
templates = Jinja2Templates(directory="templates")

exchanges = load_exchanges()


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    data: dict = {"page": "index", "instances": {}}

    data["instances"] = database.get_all_hosts(index=True)
    return templates.TemplateResponse("index.html", {"request": request, "data": data})


@app.get("/getprices")
def get_prices(
    exchange: Exchanges,
    market: Markets,
):
    if market == Markets.SPOT.value:
        return exchanges[exchange].get_spot_prices()
    elif market == Markets.FUTURES.value:
        return exchanges[exchange].get_futures_prices()
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
    elif market == Markets.FUTURES.value:
        return exchanges[exchange].get_futures_price(
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
    start_time: int | None = None,
    end_time: int | None = None,
    limit: int = 500,
    settle: Settle | None = None,
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
    if market == Markets.FUTURES.value:
        return exchanges[exchange].get_futures_kline(
            base=base.upper(),
            quote=quote.upper(),
            interval=interval,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
            settle=settle,
        )
    else:
        return {"error": "not implemented yet"}


def _auto_scrape():
    while True:
        log.info("Auto scrape routines starting")
        scraper.scrape()
        all_hosts_and_modes = database.get_hosts_and_modes()
        for exchange in all_hosts_and_modes:
            for mode in all_hosts_and_modes[exchange]:
                database.delete_then_update_price(
                    exchange=exchange,
                    market=mode,
                    data=get_prices(exchange=exchange, market=mode),
                )
        log.info(
            f"Auto scrape routines terminated. Sleeping {config.scrape_interval} seconds..."
        )
        time.sleep(config.scrape_interval)


@app.on_event("startup")
def auto_scrape():
    thread = threading.Thread(target=_auto_scrape)
    thread.daemon = True
    thread.start()
