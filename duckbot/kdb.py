import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor

from qpython.qconnection import QConnection


log = logging.getLogger('kdb')


def make_connection(host: str, port: int, username: str = None, password: str = None, auto_open=True) -> QConnection:
    log.debug(f"kdb connection {host}:{port}")
    con = QConnection(host, port, username=username, password=password, single_char_strings=True, timeout=10.0, encoding="utf-8")
    if auto_open:
        con.open()
        log.debug(f"opened kdb+ connection")
    return con


def make_connection_from_config(auto_open=True) -> QConnection:
    from .config import KDB_HOST, KDB_PORT, KDB_USER, KDB_PASS
    return make_connection(KDB_HOST, KDB_PORT, KDB_USER, KDB_PASS, auto_open=auto_open)


def ping(con: QConnection) -> bool:
    try:
        con.sendSync("1+1")
        log.debug(f"ping OK")
        return True
    except:
        log.error(f"ping FAILED")
        return False


async def query(con: QConnection, *args, **kwargs):
    def run_query():
        con.open()
        return con(*args, **kwargs)

    exec = ThreadPoolExecutor(1)
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(exec, run_query)
