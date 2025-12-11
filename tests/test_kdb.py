import os
import time
import random
import subprocess

from unittest import SkipTest

import pytest

from duckbot import kdb


KDB_Q_PATH = os.environ.get("KDB_Q_PATH")
if not KDB_Q_PATH:
    raise SkipTest("KDB_Q_PATH needs to be set")


@pytest.fixture(scope="session")
def kdb_server():
    port = 5000 + random.randint(0, 1000)
    exe = [KDB_Q_PATH, "-p", f"{port}"]

    p = subprocess.Popen(exe, cwd="/")

    time.sleep(1)  # IMPROVE: Wait for port opened...

    yield "localhost", port

    p.kill()


def test_kdb_ping(kdb_server):
    host, port = kdb_server

    con = kdb.make_connection(host, port)
    assert kdb.ping(con)


@pytest.mark.asyncio
async def test_kdb_async_query(kdb_server):
    host, port = kdb_server
    con = kdb.make_connection(host, port, auto_open=False)

    ret = await kdb.query(con, "1+1")
    assert ret == 2.0
