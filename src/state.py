import logging
from glootil import DynEnum
from enum import Enum
from db import DB

logger = logging.getLogger("state")


def to_query_arg(val):
    if isinstance(val, DynEnum):
        return val.key
    elif isinstance(val, Enum):
        return val.value
    elif val is None:
        return ''
    else:
        return val


class State:
    def __init__(self):
        self.db = DB()

    async def setup(self):
        self.pool = await self.db.start()

    async def run_query(self, query_name, **args):
        query_args = {key: to_query_arg(val) for key, val in args.items()}
        return await self.db.run_query(query_name, **query_args)

    async def search(
        self,
        query_name: str = "",
        value: str = "",
        use_fuzzy_matching: bool = True,
        limit: int = 50,
    ):
        if use_fuzzy_matching:
            value = f"%{value}%"
        logger.info("search %s, %s, limit %s", query_name, value, limit)
        return await self.run_query(query_name, value=value, limit=limit)
