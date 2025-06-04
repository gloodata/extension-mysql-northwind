import logging
import aiomysql
from glootil import DynEnum
from enum import Enum
import re
import os

logger = logging.getLogger("db")


async def start(loop=None):
    logger.info("connecting to database")

    db_host = os.environ.get("MYSQL_HOST", "localhost")
    db_port = os.environ.get("MYSQL_PORT", 3307)
    db_user = os.environ.get("MYSQL_USER", "root")
    db_password = os.environ.get("MYSQL_PASSWORD", "supersecret")
    db_name = os.environ.get("MYSQL_DATABASE", "northwind")

    db_autocommit = True
    db_min_size = 1
    db_max_size = 5

    pool = await aiomysql.create_pool(
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

    return pool


async def stop(pool):
    logger.info("disconnecting from database")

    if pool:
        pool.close()
        await pool.wait_closed()
        logger.info("disconnected from database")
    else:
        logger.warning("no database connection")


async def select_one_cur(cur, query, args):
    await cur.execute(query, args)
    return await cur.fetchone()


async def select_many_cur(cur, query, args):
    await cur.execute(query, args)
    return await cur.fetchall()


async def select_one_list(pool, query, *args):
    return await with_cursor(pool, select_one_cur, query, args)


async def select_many_list(pool, query, *args):
    return await with_cursor(pool, select_many_cur, query, args)


async def select_one(pool, query, **args):
    return await with_cursor(pool, select_one_cur, query, args)


async def select_many(pool, query, **args):
    return await with_cursor(pool, select_many_cur, query, args)


async def with_cursor(pool, fn, query, args):
    query_args = {key: to_query_arg(val) for key, val in args.items()}
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            return await fn(cur, query, query_args)


def to_query_arg(val):
    if isinstance(val, DynEnum):
        return val.name
    elif isinstance(val, Enum):
        return val.value
    elif val is None:
        return ""
    else:
        return val


async def select_cursor(conn, query, parameters):
    cur = await conn.cursor()
    await cur.execute(query, parameters)
    return cur


async def execute(conn, query, parameters):
    async with conn.cursor() as cur:
        await cur.execute(query, parameters)
        return cur.rowcount


def process_sql(query_fqn, qop, sql) -> str:
    if re.search(r"%\(\w+\)s", sql):
        logger.warning(f"Found an old SQL parameter format in query {query_fqn}: {sql}")

    # Replace :param with %(param)s
    sql = re.sub(r":(\w+)", r"%(\1)s", sql)
    return sql


class DriverAdapter:
    def __init__(self):
        self.select_one = select_one
        self.select_all = select_many
        self.select_cursor = select_cursor
        self.execute = execute
        self.process_sql = process_sql


def get_driver_adapter():
    return DriverAdapter()
