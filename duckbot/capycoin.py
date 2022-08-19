from typing import List, Dict

import logging
import sqlite3

from discord import User

import requests

from .config import CAPYCOIN_HOST, CAPYCOIN_USERS_DB_PATH


log = logging.getLogger('capycoin')


class Token(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token
    def __call__(self, r):
        r.headers["authorization"] = f"Bearer {self.token}"
        return r


def endpoint_url(path: str) -> str:
    base = CAPYCOIN_HOST
    assert base, "`CAPYCOIN_HOST` is not set!"
    if base.endswith("/"):
        base = base[:-1]
    return f"{base}{path}"


def request(method, endpoint, token=None, json=None):
    l = log.getChild(endpoint)
    try:
        kwargs={}
        if token:
            kwargs['auth'] = Token(token)
        if json:
            kwargs['json'] = json

        url = endpoint_url(endpoint)

        l.debug(f"Request: `{url}` JSON: `{json}`")

        r = requests.request(method, url, **kwargs)
        if not r.ok:
            l.warning(f'Response not OK: {r} {r.reason} {r.content}')
            return None
        return r.json()
    except Exception as err:
        l.error(f'Exception making request: {err}')
        return None


def connect() -> sqlite3.Connection:
    l = log.getChild('connect')
    try:
        con = sqlite3.connect(CAPYCOIN_USERS_DB_PATH)
        con.cursor().execute("SELECT 1+1")
        return con
    except Exception as err:
        l.error(f"Could not connect: {err}")
        return None


def create_account() -> Dict:
    return request('post', '/account')


def get_account(account_id: str, token=None) -> Dict:
    return request('get', f"/account/{account_id}", token=token)


def get_funds(account_id: str, token=None) -> int:
    if d := get_account(account_id, token=token):
        return d['funds']


def create_transaction(account_id: str, receiver_account_id: str, amount: int, token=None) -> Dict:
    json={'receiver': receiver_account_id, 'amount': amount}
    return request('post', f"/account/{account_id}/transaction", token=token, json=json)


def get_transactions(account_id: str, token=None) -> List[Dict]:
    return request('get', f"/account/{account_id}/transactions", token=token)


def create_user_table(con: sqlite3.Connection):
    con.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            account_id STRING,
            token STRING
        )
    """)
    con.execute("""CREATE INDEX IF NOT EXISTS users_account_id_idx ON users (account_id)""")


def load_account_for_discord_user(con: sqlite3.Connection, user: User) -> str:
    l = log.getChild(f"account_id_for_discord_user.{user}")
    try:
        rows = con.cursor().execute("SELECT account_id, token FROM users WHERE user_id = (?)", [user.id]).fetchone()
        if rows is None:
            return None
        return rows
    except Exception as err:
        l.error(f"Exception during query: {err}")
        return None


def save_account_for_discord(con: sqlite3.Connection, user: User, account_id: str, token: str):
    l = log.getChild(f"account_id_for_discord_user.{user}")
    assert account_id, "Need `account_id`"
    assert token, "Need `token`"
    try:
        con.cursor().execute("INSERT INTO users VALUES (?, ?, ?)", [user.id, account_id, token])
        con.commit()
        return True
    except Exception as err:
        l.error(f"Exception during query: {err}")
        return False


async def action_signup(user: User) -> str:
    con = connect()
    if not con:
        return "Unfortunately, I couldn't action your command!"
    if ret := load_account_for_discord_user(con, user):
        return "You already have an account"
    if ret := create_account():
        account_id = ret["account_id"]
        token = ret["token"]
        if not save_account_for_discord(con, user, account_id, token):
            return "Unfortunately, saving your information failed!"
        await user.send(f"Your account id is: `{account_id}`\nYour account security token is: ```{token}```\nThis token can be used to interact with the CapyCoin gateway directly.")
        return "🪙 Registered account!"
    else:
        return "Unfortunately, account registration failed!"


async def action_funds(user: User) -> str:
    con = connect()
    if not con:
        return "Unfortunately, I couldn't action your command!"
    if ret := load_account_for_discord_user(con, user):
        account_id, token = ret
        funds = get_funds(account_id, token)
        if funds is None:
            return "Unfortunately, I could not retrieve information about your funds!"
        else:
            return f"🪙 You have {funds} coin, {user.mention}"
    else:
        return "I couldn't find you in the system. Do you have an account?"


async def action_send(user: User, target_user: User, amount: str) -> str:
    try:
        amount = int(amount)
    except:
        return "The `amount` should be a whole number"

    if amount > 100:
        return "That amount exceeds the hard coded limit!"

    con = connect()
    if not con:
        return "Unfortunately, I couldn't action your command!"

    send_info = load_account_for_discord_user(con, user)
    recv_info = load_account_for_discord_user(con, target_user)

    if not send_info:
        return "I couldn't find you in the system. Do you have an account?"
    if not recv_info:
        return f"I couldn't find {target_user.mention} in the system. Do they have an account?"

    account_id, token = send_info
    recv_account_id, _ = recv_info

    if ret := create_transaction(account_id, recv_account_id, amount, token):
        tx_id = ret['transaction_id']
        await target_user.send(f"🪙 {user.mention} has sent you {amount}! For your reference, the transaction id is: `{tx_id}`")
        return f"🪙  {user.mention} sent {amount} to {target_user.mention}"
    else:
        return "Unfortunately, the transaction could not be processed!"


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    log.info("Creating Tables!")
    con = connect()
    create_user_table(con)
    con.close()
