import os

TOKEN = os.environ.get("DUCKBOT_TOKEN", "")

LANGUAGE_MODEL = os.environ.get("DUCKBOT_LANG_MODEL", "en_core_web_md")

KDB_HOST = os.environ.get("KDB_HOST", "localhost")
KDB_PORT = int(os.environ.get("KDB_PORT", 5000))
KDB_USER = os.environ.get("KDB_USER")
KDB_PASS = os.environ.get("KDB_PASS")

FORTUNE_PATH = os.environ.get("FORTUNE_PATH", "/usr/games/fortune")

CAPYCOIN_HOST = os.environ.get("CAPYCOIN_HOST")
CAPYCOIN_USERS_DB_PATH = os.environ.get("CAPYCOIN_USERS_DB_PATH", "users.db3")