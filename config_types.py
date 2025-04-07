from typing import List, TypedDict


class AppConfig(TypedDict):
    LEDGERBASE_SECRET_KEYS: List[str]
