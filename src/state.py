import logging
import db
from db import select_many, select_one, get_driver_adapter
import aiosql

logger = logging.getLogger("state")


class State:
    def __init__(self):
        self.pool = None

    async def setup(self):
        self.pool = await db.start()
        aiosql.register_adapter("aiomysql", get_driver_adapter)
        self.queries = aiosql.from_path("queries.sql", "aiomysql")

    def get_query(self, query_name):
        return getattr(self.queries, query_name).sql

    def get_queries(self):
        queries_combined = ""
        for query_name in dir(self.queries):
            if query_name.startswith("select_"):  # Skip internal attributes
                query_sql = getattr(self.queries, query_name).sql
                queries_combined += f"-- name: {query_name}\n{query_sql}\n"
        return queries_combined

    async def select_many(self, query_name, **kwargs):
        query = self.get_query(query_name)
        return await select_many(self.pool, query, **kwargs)

    async def select_one(self, query_name, **kwargs):
        query = self.get_query(query_name)
        return await select_one(self.pool, query, **kwargs)

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
        if limit == 1:
            return await self.select_one(query_name, value=value, limit=limit)
        else:
            return await self.select_many(query_name, value=value, limit=limit)
