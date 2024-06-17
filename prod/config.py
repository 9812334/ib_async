import os

SCRIPT_DIR = os.getcwd()

LOGS_DIR = f"{SCRIPT_DIR}/logs"
CHANIFY_URL = "https://api.chanify.net/v1/sender/"
CHANIFY_TOKEN = "CICswLUGEiJBQUZIR0pJQ0VVNkxUTlZCMk1DRElCWU1RSlNWMktCS0NFIgIIAQ.vj8gcfxM4jD9Zv0mBMSlFlY51EL_jC5dB8LWdWX1tAs"

IBKR_ACCOUNT_1 = "U10394496"
IBKR_ACCOUNT_2 = "U2340948"

IBKR_SERVER = "192.168.1.36"  # "127.0.0.1"
IBKR_PORT = 4001

import random
CLIENT_ID = random.randint(1, 99)

SELL_SCALP = {
    "margin_cushion_pct": 0,
    "account": IBKR_ACCOUNT_1,
    "push": True,
    "open_push": True,
    "modify_push": True,
    "close_push": True,
    "strategy": "SELL TO OPEN SCALP",
    "contract": "NQU2024",
    "contract_id": 637533450,
    "tick_increment": 0.25,
    "open_permid": None,
    "close_permid": None,
    "open_qty": 1,
    "open_type": "LIMIT",
    "open_action": "SELL",
    "open_ref": "ask",
    "open_ticks": 5,
    "close_qty": 1,
    "close_type": "LIMIT",
    "close_action": "BUY",
    "close_ref": "open_fill",
    "close_ticks": -10,
    "pause_replace": 40,
    "pause_restart": 10,
}

BUY_SCALP = {
    "margin_cushion_pct": 5,
    "account": IBKR_ACCOUNT_1,
    "push": True,
    "open_push": True,
    "modify_push": False,
    "close_push": True,
    "strategy": "BUY TO OPEN SCALP",
    "contract": "NQU2024",
    "contract_id": 637533450,
    "tick_increment": 0.25,
    "open_permid": 519029452,
    "close_permid": 519029476,
    "open_qty": 1,
    "open_type": "LIMIT",
    "open_action": "BUY",
    "open_ref": "ask",
    "open_ticks": -5,
    "close_qty": 1,
    "close_type": "LIMIT",
    "close_action": "SELL",
    "close_ref": "open_fill",
    "close_ticks": 10,
    "pause_replace": 50,
    "pause_restart": 20,
}

DEBUG = False
LIVE = True
STRATEGY = BUY_SCALP
PUSH = True


ORDER_COLS = [
    "localSymbol",
    "permId",
    "status",
    "orderType",
    "action",
    "lmtPrice",
    "remaining",
]

TRADE_COLS = [
    "permId",
    "clientId",
    "localSymbol",
    "status",
    "orderType",
    "action",
    "lmtPrice",
    "remaining",
    "filledQuantity",
    "fills",
]

# OPEN_TRADE_COLS = [
#     "permId",
#     "orderId",
#     "symbol",
#     "lastTradeDateOrContractMonth",
#     "orderType",
#     "action",
#     "lmtPrice",
#     "totalQuantity",
#     "remaining",
#     "fills",
#     "log",
# ]


OPEN_TRADE_COLS = [
    "permId",
    "orderId",
    "symbol",
    "lastTradeDateOrContractMonth",
    "orderType",
    "action",
    "lmtPrice",
    "totalQuantity",
    "remaining",
]
