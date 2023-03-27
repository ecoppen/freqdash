<h1 align="center">
<img src="https://user-images.githubusercontent.com/51025241/209450888-c9160c81-38d8-44dd-93d9-96b4a6922074.png">
</h1>

<p align="center">
A python (3.11+) and Fastapi script to display a dashboard for your <a target="_blank" href="https://www.freqtrade.io/en/stable/">Freqtrade</a> instances(s) via SSH.
</p>
<p align="center">
<img alt="GitHub Pipenv locked Python version" src="https://img.shields.io/github/pipenv/locked/python-version/ecoppen/freqdash"> 
<a href="https://github.com/ecoppen/freqdash/blob/main/LICENSE"><img alt="License: GPL v3" src="https://img.shields.io/badge/License-GPLv3-blue.svg">
<a href="https://app.fossa.com/projects/git%2Bgithub.com%2Fecoppen%2Ffreqdash?ref=badge_shield"><img alt="FOSSA Status" src="https://app.fossa.com/api/projects/git%2Bgithub.com%2Fecoppen%2Ffreqdash.svg?type=shield"></a>
<a href="https://codecov.io/gh/ecoppen/freqdash"><img src="https://codecov.io/gh/ecoppen/freqdash/branch/main/graph/badge.svg?token=4XCZZ6MFPH"/></a>
<a href="https://codeclimate.com/github/ecoppen/freqdash/maintainability"><img src="https://api.codeclimate.com/v1/badges/c5663e3c743c988ea0e1/maintainability" /></a>
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
</p>

freqdash is a free and open source python (3.11+) script to display a dashboard for your <a target="_blank" href="https://www.freqtrade.io/en/stable/">Freqtrade</a> instances(s). 
It is built on the <a target="_blank" href="https://fastapi.tiangolo.com/">FastApi</a> framework and connects to local/remote Freqtrade instances via the <a target="_blank" href="https://www.paramiko.org/">paramiko</a> SSH library before consuming the local API, storing the data and displaying everything on one dashboard.
freqdash also has the ability to connect directly to Exchange APIs for price data and kline information. 

![image](https://user-images.githubusercontent.com/51025241/226862169-bc2d8767-d453-4e41-9bcc-77463a4e0329.png)

## Features
- Monitoring: Each freqtrade instance can be monitored centrally whether hosted locally or remotely
- Charts: Profit/Loss, portfolio, kline with entries/exits charts available for each instance and exchange
- Direct exchange data: Spot and futures pair prices and klines accessible directly from the exchange

### Exchange support
| Exchange | Direct data | News |
|:--------:|:-----------:|:----:|
|  Binance |      ✅      |   ✅  |
|   Bybit  |      ✅      |   ✅  |
|  Gate.io |      ✅      |   ➖  |
|  Kucoin  |      ✅      |   ➖  |
|    Okx   |      ✅      |   ✅  |

## Quickstart

- Clone the repo `git clone https://github.com/ecoppen/freqdash.git`
- Navigate to the repo root `cd freqdash`
- Navigate to the config folder `cd config`
- Create the config file from template `cp config.json.example config.json`
- Populate the `config.json` files as required using a text editor e.g. `nano config.json`
- Navigate back to the repo root `cd ..`
- Install pipenv `pip install pipenv`
- Install required packages `pipenv install`
- Activate the environment `pipenv shell`
- Start the webserver in development mode `uvicorn freqdash.main:app --reload`

### Developers
- Install developer requirements from pipenv `pipenv install --dev`
- Install pre-commit hooks `pre-commit install`


## License
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Fecoppen%2Ffreqdash.svg?type=large)](https://app.fossa.com/projects/git%2Bgithub.com%2Fecoppen%2Ffreqdash?ref=badge_large)
