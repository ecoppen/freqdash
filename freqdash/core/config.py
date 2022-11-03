import json

from pydantic import BaseModel, Extra, Field, IPvAnyAddress, ValidationError, validator


class FreqtradeAPI(BaseModel):
    ssh_host: IPvAnyAddress  # type: ignore
    ssh_port: int = Field(5432, ge=1, le=65535)
    ssh_username: str
    ssh_password: str
    remote_host: IPvAnyAddress = IPvAnyAddress.validate("127.0.0.1")
    remote_port: int = Field(5432, ge=1, le=65535)
    api_username: str
    api_password: str


class Config(BaseModel):
    freqtrade_instances: list[FreqtradeAPI]
    scrape_interval: int = 600

    @validator("scrape_interval")
    def interval_amount(cls, v):
        if v < 300:
            raise ValueError("Scraping interval lower limit is 300 (5 minutes)")
        return v


def load_config(path):
    if not path.is_file():
        raise ValueError(f"{path} does not exist")
    else:
        f = open(path)
        try:
            data = json.load(f)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"ERROR: Invalid JSON: {exc.msg}, line {exc.lineno}, column {exc.colno}"
            )
        try:
            return Config(**data)
        except ValidationError as e:
            raise ValueError(f"{e}")
