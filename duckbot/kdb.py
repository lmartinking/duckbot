import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor

from kola import Q


log = logging.getLogger("kdb")


class QConnection:
    def __init__(
        self,
        host: str,
        port: int,
        username: str = None,
        password: str = None,
        timeout: int = 0,
    ):
        if username and password:
            self.con = Q(host, port, username, password)
        else:
            self.con = Q(host, port)

    def open(self):
        return self.con.connect()

    def close(self):
        return self.con.disconnect()

    def _encode_arg(self, arg):
        if isinstance(arg, str):
            return arg.encode("utf-8")
        if isinstance(arg, (list, tuple)):
            return [self._encode_arg(a) for a in arg]
        return arg

    def _encode_args(self, args):
        return [self._encode_arg(a) if i > 0 else a for i, a in enumerate(args)]

    def sync(self, *args):
        args = self._encode_args(args)
        return self.con.sync(*args)

    def asyn(self, *args):
        args = self._encode_args(args)
        return self.con.asyn(*args)

    def __call__(self, *args):
        return self.sync(*args)


def make_connection(host: str, port: int, username: str = None, password: str = None, auto_open=True) -> QConnection:
    log.debug(f"kdb connection {host}:{port}")
    con = QConnection(host, port, username=username, password=password, timeout=1)
    if auto_open:
        con.open()
        log.debug(f"opened kdb+ connection")
    return con


def make_connection_from_config(auto_open=True) -> QConnection:
    from .config import KDB_HOST, KDB_PORT, KDB_USER, KDB_PASS

    return make_connection(KDB_HOST, KDB_PORT, KDB_USER, KDB_PASS, auto_open=auto_open)


def ping(con: QConnection) -> bool:
    try:
        con.sync("1+1")
        log.debug(f"ping OK")
        return True
    except:
        log.error(f"ping FAILED")
        return False


async def query(con: QConnection, *args):
    def run_query():
        con.open()
        return con.sync(*args)

    exec = ThreadPoolExecutor(1)
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(exec, run_query)
