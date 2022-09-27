from freqdash.exchange.binance import Binance
from freqdash.exchange.bybit import Bybit
from freqdash.exchange.gateio import Gateio
from freqdash.exchange.kucoin import Kucoin
from freqdash.exchange.okx import Okx


def load_exchanges():
    return {
        "binance": Binance(),
        "bybit": Bybit(),
        "gateio": Gateio(),
        "kucoin": Kucoin(),
        "okx": Okx(),
    }
