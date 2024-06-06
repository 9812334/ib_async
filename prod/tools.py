import argparse
import importlib
import datetime
import socket
import random
import datetime
import os
import pandas as pd
import sys

from ib_async import *

import platform
import chime
import datetime
import os

import urllib

def chime_success():
    if platform.system() == "Linux":
        chime.success()
    elif platform.system() == "Darwin":
        os.system("say beep")
    elif platform.system() == "Windows":
        raise Exception("not handled yet")
    
    return True



def alert(success=True):
    if platform.system() == "Linux":
        if success:
            chime.success()
        else:
            chime.warning()
    elif platform.system() == "Darwin":
        os.system("say beep")
    elif platform.system() == "Windows":
        raise Exception("not handled yet")
    
    return True


def beep(alert = 0):
    if platform.system() == "Linux":
        if alert == 0:
            chime.success()
        else:
            chime.warning()
    elif platform.system() == "Darwin":
        os.system("say beep")
    elif platform.system() == "Windows":
        raise Exception("not handled yet")
    
    return True

def push_notifications(msg="Hello world!", push = True, sound = 0):
    body = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(body)

    if sound > 0:
        beep(sound)
    
    # https://api.chanify.net/v1/sender/<token>?sound=1&priority=10&title=hello
    
    if push:
        try:
            data = urllib.parse.urlencode({"text": body}).encode()
            req = urllib.request.Request(
                "https://api.chanify.net/v1/sender/CICswLUGEiJBQUZIR0pJQ0VVNkxUTlZCMk1DRElCWU1RSlNWMktCS0NFIgIIAQ.vj8gcfxM4jD9Zv0mBMSlFlY51EL_jC5dB8LWdWX1tAs",
                data=data,
            )
            response = urllib.request.urlopen(req)
            response.read()  # Read the response to ensure the request is complete
        except urllib.error.URLError as e:
            print(f"Error sending request: {e.reason}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        
    return True



util.logToFile(f"{datetime.datetime.now().strftime('%Y-%m-%d')}-{socket.gethostname()}.log")
util.startLoop()
util.logToConsole()

if "ib" in globals():
    ib.disconnect()

randint = lambda a=1, b=10: random.randint(a, b)
ib = IB()
# ib.connect("127.0.0.1", 4001, randint(1, 99))
ib.connect("192.168.1.36", 4001, randint(1, 99))

ib.reqAccountSummary() # run only once
ib.reqAllOpenOrders()
ib.reqPositions()


NQM4 = Contract(conId=620730920)
ib.qualifyContracts(NQM4)
ticker = ib.reqMktDepth(contract=NQM4, isSmartDepth=True)

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

def get_trade_by_permid(permid):
    return next((trade for trade in ib.trades() if trade.order.permId == permid), None)


def get_last_trade_permid(n = -1):
    try:
        return ib.trades()[n].order.permId
    except IndexError:
        return None

def get_last_trade():
    try:
        last_trade_permid = ib.executions()[-1].permId
        return get_trade_by_permid(last_trade_permid)
    except IndexError:
        return None

def get_cancelled_orders():
    return [trade for trade in ib.trades() if trade.fills != []]


def get_last_executed_trade(n = -1):
    try:
        return get_trade_by_permid(permid = (ib.executions()[n].permId))
    except IndexError:
        return None

def print_line(n = 50):
    print(f"-" * n)


def print_clear():
    os.system("cls" if os.name == "nt" else "clear")

def print_account_summary(accounts = ["U10394496", "U2340948"]):

    for account in accounts:
        print(f"Account: {account}")

        for item in ib.accountSummary(account=account):
            if item.tag in [
                "Account",
                "Cushion",
                "NetLiquidation",
                "TotalCashValue",
                "LookAheadExcessLiquidity",
            ]:
                print(item.tag, item.value)

def print_executions(cols = ["time", "side", "price", "permId", "shares"], tail = 5):
    executions_df = util.df(ib.executions())
    
    if executions_df is not None:
        print(f"Executions: {len(executions_df)}")
    
        if len(executions_df) > 0:
            print(executions_df[cols].tail(tail))

    return executions_df

    
def print_openOrders(cols = ["localSymbol", "permId", "action", "totalQuantity", "orderType", "lmtPrice", "tif", "status"]):

    open_orders_df = util.df(parse_ibrecords(ib.reqAllOpenOrders()))
    
    print(f"Open Orders: {len(open_orders_df)}")
    print(open_orders_df[cols])

    return open_orders_df

def print_openTrades():
    open_trades = ib.openTrades()

    open_trades_df = util.df([t.order for t in ib.openTrades()]).loc[
        :,
        [
            "orderId",
            "permId",
            "action",
            "totalQuantity",
            "orderType",
            "lmtPrice",
        ],
    ]

    print(f"Open Trades: {len(open_trades_df)}")

    if open_trades != []:
        print(
            open_trades_df
        )

    return open_trades


def print_orderbook():
    if ticker is not None and ticker.domBids is not None and ticker.domAsks is not None:
        max_length = max(len(ticker.domBids), len(ticker.domAsks))
        for i in range(max_length):
            bid_size = ticker.domBids[i].size if i < len(ticker.domBids) else "-"
            bid_price = ticker.domBids[i].price if i < len(ticker.domBids) else "-"
            ask_price = ticker.domAsks[i].price if i < len(ticker.domAsks) else "-"
            ask_size = ticker.domAsks[i].size if i < len(ticker.domAsks) else "-"
            print(f"{bid_size:>8} {bid_price:>10} | {ask_price:<10} {ask_size:<8}")


def print_order(o):
    if o is None:
        print()
        return

    order = o.order
    contract = o.contract
    orderStatus = o.orderStatus

    print(f"symbol\tpermId\t\tstatus\t\taction\tfilled\tremaining\tlmtPrice")

    print(
        f"{contract.symbol}\t{order.permId}\t{orderStatus.status}\t{order.action}\t{orderStatus.filled}\t{orderStatus.remaining}\t\t{order.lmtPrice}\t"
    )



def print_positions(contract = None, header = True):
    if header:
        print(f"Positions: ")
        
    if contract:        
        positions = [pos for pos in ib.positions() if pos.contract == contract]
    else:
        positions = [pos for pos in ib.positions()]

    for f in positions:
        print(
            f"{f.contract.symbol}\t{f.position} @ {f.avgCost/round(float(f.contract.multiplier or 1),2)}"
        )

    return util.df([p for p in positions])

def parse_ibrecords(data_array):

    data_list = []

    for obj in data_array:
        data = {}

        if hasattr(obj, "contract"):
            util.logging.debug(obj.contract)
            contract = util.dataclassNonDefaults(obj.contract)
            data = {**data, **contract}

        if hasattr(obj, "order"):
            util.logging.debug(obj.order)
            order = util.dataclassNonDefaults(obj.order)
            order.pop("softDollarTier")
            data = {**data, **order}

        if hasattr(obj, "orderStatus"):
            util.logging.debug(obj.orderStatus)
            orderStatus = util.dataclassNonDefaults(obj.orderStatus)
            data = {**data, **orderStatus}

        if hasattr(obj, "fills"):
            util.logging.debug(obj.fills)
            fills = {"fills": obj.fills}
            data = {**data, **fills}

        if hasattr(obj, "log"):
            util.logging.debug(obj.log)
            logs = {"log": [util.dataclassAsDict(e) for e in obj.log]}
            data = {**data, **logs}

        if hasattr(obj, "advancedError"):
            util.logging.debug(obj.advancedError)
            advancedError = {"advancedError": obj.advancedError}
            data = {**data, **advancedError}

        if type(obj) == Order:
            util.logging.debug(obj)
            order = util.dataclassNonDefaults(obj)
            order.pop("softDollarTier")
            data = {**data, **order}

        data_list.append(data)

    return data_list




def print_ibrecords(
    data_array,
    cols,
):
    df = util.df(data_array)
    df = df[cols]
    print(df)


if __name__ == "__main__":
    print_clear()
    print_account_summary()
    print_executions()
    print_openOrders()
    print_openTrades()
    print_positions()
    print_orderbook()

