import logging
import os

import aiomysql
import aiosql

logger = logging.getLogger("db")


class DB:
    def __init__(self):
        self.queries = aiosql.from_path("queries.sql", "mysql-connector")

    async def start(self, loop=None):
        logger.info("connecting to database")

        db_host = os.environ.get("MYSQL_HOST", "localhost")
        db_port = os.environ.get("MYSQL_PORT", 3307)
        db_user = os.environ.get("MYSQL_USER", "root")
        db_password = os.environ.get("MYSQL_PASSWORD", "supersecret")
        db_name = os.environ.get("MYSQL_DATABASE", "northwind")

        db_autocommit = True
        db_min_size = 1
        db_max_size = 5

        self.pool = await aiomysql.create_pool(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            db=db_name,
            autocommit=db_autocommit,
            minsize=db_min_size,
            maxsize=db_max_size,
            loop=loop,
        )

        logger.info("connected to database")

    async def stop(self, pool):
        logger.info("disconnecting from database")

        if pool:
            await pool.close()
            logger.info("disconnected from database")
        else:
            logger.warning("no database connection")

    async def run_query(self, query_name, **args):
        query = getattr(self.queries, query_name)
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(query.sql, args)
                return await cur.fetchall()
