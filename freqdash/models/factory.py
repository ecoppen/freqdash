import logging
import secrets
from pathlib import Path

from freqdash.models.database import Database

log = logging.getLogger(__name__)


def load_databases():
    databases = {}
    data_folder = Path(Path().resolve(), "data")
    for file in sorted(data_folder.glob("*.sqlite")):
        if file.stem in databases:
            log.error(
                f"There are multiple databases named: {file.name}. This will be given a random name until you fix."
            )
            databases[f"{file.stem}-{secrets.token_hex()}"] = Database(path=file)
        else:
            databases[file.stem] = Database(path=file)

    return databases
