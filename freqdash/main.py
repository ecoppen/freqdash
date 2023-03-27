from __future__ import annotations

import logging
import os
import threading
import time
from datetime import date, datetime
from datetime import time as dt_time
from datetime import timedelta
from pathlib import Path

from fastapi import FastAPI
from fastapi import Path as fPath
from fastapi import Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from freqdash.connection.factory import load_tunnels
from freqdash.core.config import load_config
from freqdash.core.utils import dt_to_ts
from freqdash.exchange.factory import load_exchanges
from freqdash.exchange.utils import Exchanges, Intervals, Markets, Settle
from freqdash.models.database import Database
from freqdash.scraper.scraper import Scraper

ssh_keys_folder = Path(Path().resolve(), "ssh_keys")
config_file = Path(Path().resolve(), "config", "config.json")
config = load_config(path=config_file)

logs_file = Path(Path().resolve(), "log.txt")
logs_file.touch(exist_ok=True)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=os.environ.get("LOGLEVEL", config.log_level.upper()),
    handlers=[logging.FileHandler(logs_file), logging.StreamHandler()],
)

log = logging.getLogger(__name__)
log.info("freqdash started")

database = Database(config=config.database)
tunnels = load_tunnels(
    config=config.remote_freqtrade_instances, ssh_keys_folder=ssh_keys_folder
)
scraper = Scraper(tunnels=tunnels, database=database)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(GZipMiddleware)
templates = Jinja2Templates(directory="templates")

exchanges = load_exchanges()


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def index(request: Request):
    page_data = {"dashboard_title": config.dashboard_name, "year": date.today().year}
    data: dict = {"page": "index", "instances": database.get_all_hosts(index=True)}

    now = datetime.now()
    one_hour_ago = now - timedelta(hours=1)
    today_start = datetime.combine(datetime.today(), dt_time.min)
    all_time = now - timedelta(weeks=104)

    news: dict = {
        "1h": database.get_count_news_items(
            start=dt_to_ts(one_hour_ago), end=dt_to_ts(now)
        ),
        "1d": database.get_count_news_items(
            start=dt_to_ts(today_start), end=dt_to_ts(now)
        ),
        "all": database.get_count_news_items(
            start=dt_to_ts(all_time), end=dt_to_ts(now)
        ),
    }
    without_links = [data["instances"]["open"], data["instances"]["recent"]]
    for data_structure in without_links:
        for trade in data_structure:
            if trade[23] == "SPOT":
                link = exchanges[trade[5]].spot_trade_url
            else:
                link = exchanges[trade[5]].futures_trade_url
            link = link.replace("BASE", trade[3]).replace("QUOTE", trade[4])
            trade += [link]
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "data": data, "news": news, "page_data": page_data},
    )


@app.get(
    "/instance/{instance_id}", response_class=HTMLResponse, include_in_schema=False
)
def instance(
    request: Request,
    instance_id: int = fPath(title="The ID of the account to get", gt=0),
):
    account = database.get_instance(instance_id=instance_id)
    if not account:
        return RedirectResponse("/")

    page_data = {"dashboard_title": config.dashboard_name, "year": date.today().year}
    return templates.TemplateResponse(
        "account.html", {"request": request, "page_data": page_data, "account": account}
    )


@app.get("/news", response_class=HTMLResponse, include_in_schema=False)
def news(
    request: Request,
    exchange: Exchanges | None = None,
    start: int | None = None,
    end: int | None = None,
):
    page_data = {"dashboard_title": config.dashboard_name, "year": date.today().year}
    news = get_news(exchange=exchange, start=start, end=end)

    return templates.TemplateResponse(
        "news.html", {"request": request, "page_data": page_data, "news": news}
    )


@app.get("/getnews")
def get_news(
    exchange: Exchanges | None = None, start: int | None = None, end: int | None = None
):
    return database.get_news_items(start=start, end=end, exchange=exchange)


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

        for exchange in config.news_source:
            log.info(f"Scraping news from {exchange}")
            news = exchanges[exchange].get_news()
            database.delete_then_update_news(exchange=exchange, data=news)

        # scraper.scrape()
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
