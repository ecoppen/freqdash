import json
from enum import Enum

from pydantic import (
    BaseModel,
    Field,
    IPvAnyAddress,
    ValidationError,
    root_validator,
    validator,
)


class Databases(Enum):
    POSTGRES = "postgres"
    SQLITE = "sqlite"


class Database(BaseModel):
    engine: str = Databases.SQLITE.value  # type: ignore
    username: str | None
    password: str | None
    host: IPvAnyAddress = IPvAnyAddress.validate("127.0.0.1")  # type: ignore
    port: int = Field(5432, ge=1, le=65535)
    name: str = "freqdash"


class LocalFreqtradeAPI(BaseModel):
    local_host: IPvAnyAddress = IPvAnyAddress.validate("127.0.0.1")
    local_port: int = Field(5432, ge=1, le=65535)
    api_username: str = Field(min_length=1)
    api_password: str = Field(min_length=1)


class RemoteFreqtradeAPI(BaseModel):
    ssh_host: IPvAnyAddress  # type: ignore
    ssh_port: int = Field(5432, ge=1, le=65535)
    ssh_username: str | None
    ssh_pkey_filename: str | None
    ssh_password: str = Field(min_length=1)
    remote_host: IPvAnyAddress = IPvAnyAddress.validate("127.0.0.1")
    remote_port: int = Field(5432, ge=1, le=65535)
    api_username: str = Field(min_length=1)
    api_password: str = Field(min_length=1)

    @root_validator
    def check_username_or_pkey(cls, values):
        username, pkey = values.get("ssh_username"), values.get("ssh_pkey_filename")
        if username is None and pkey is None:
            raise ValueError("Username or pkey must be provided")
        return values


class Config(BaseModel):
    local_freqtrade_instances: list[LocalFreqtradeAPI] | None
    remote_freqtrade_instances: list[RemoteFreqtradeAPI] | None
    scrape_interval: int = 600
    database: Database

    @validator("scrape_interval")
    def interval_amount(cls, v):
        if v < 60:
            raise ValueError("Scraping interval lower limit is 60 (1 minute)")
        return v

    @root_validator
    def check_instance_exists(cls, values):
        local, remote = values.get("local_freqtrade_instances"), values.get(
            "remote_freqtrade_instances"
        )
        if local is None and remote is None:
            raise ValueError("No freqtrade instance found either for remote or local")
        return values


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
