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

from alerts import *


util.logToFile(f"{datetime.datetime.now().strftime('%Y-%m-%d')}-{socket.gethostname()}.log")
util.startLoop()
util.logToConsole()

if "ib" in globals():
    ib.disconnect()

randint = lambda a=1, b=10: random.randint(a, b)
ib = IB()
ib.connect("127.0.0.1", 4001, randint(1, 99))

# NQM2024 contract
print(f"Setting contract to NQM2024 symbol / JUN 2024 / Contract(conId=620730920)")
NQM4 = Contract(conId=620730920)
ib.qualifyContracts(NQM4)

ticker = ib.reqMktDepth(contract=NQM4, isSmartDepth=True)

# account info
ib.reqAllOpenOrders()
ib.reqAccountSummary()
ib.reqPositions()

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

def print_executions():
    executions = ib.executions()
    print(f"Intraday Executions: {len(executions)}")

    if len(executions) > 0:
        print(
            util.df(ib.executions()).tail().loc[
                :, ["time", "side", "price", "permId", "shares"]
            ]
        )

    return executions


def print_openOrders():
    open_orders = ib.openOrders()
    open_orders_df = util.df(open_orders).sort_values("lmtPrice", ascending=False).loc[
                :,
                [
                    "orderId",
                    "permId",
                    "action",
                    "totalQuantity",
                    "orderType",
                    "lmtPrice",
                    "tif",
                ],
            ]

    print(f"Open Orders: {len(open_orders_df)}")

    if open_orders != []:
        print(
            open_orders_df
        )
       
    return open_orders

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



def parse_ibrecords(
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

