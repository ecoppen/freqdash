import logging
import os
from pathlib import Path
from typing import Union

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from freqdash.exchange.binance import Binance
from freqdash.exchange.bybit import Bybit
from freqdash.exchange.gateio import Gateio
from freqdash.exchange.kucoin import Kucoin
from freqdash.exchange.okx import Okx
from freqdash.exchange.utils import Exchanges, Markets

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

exchanges = {
    "binance": Binance(),
    "bybit": Bybit(),
    "gateio": Gateio(),
    "kucoin": Kucoin(),
    "okx": Okx(),
}


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    data = {"page": "index"}
    return templates.TemplateResponse("index.html", {"request": request, "data": data})


@app.get("/page/{page_name}", response_class=HTMLResponse)
def page(request: Request, page_name: str):
    data = {"page": page_name}
    return templates.TemplateResponse("index.html", {"request": request, "data": data})


@app.get("/getprices/{exchange}/{market}")
def get_prices(
    exchange: Exchanges,
    market: Markets,
    base: Union[str, None] = None,
    stake: Union[str, None] = None,
):
    return exchanges["binance"].get_spot_prices()


@app.get("/getprice/{exchange}/{market}/{base}/{stake}")
def get_price(
    exchange: Exchanges,
    market: Markets,
    base: Union[str, None] = None,
    stake: Union[str, None] = None,
):
    return exchanges["binance"].get_spot_prices()
