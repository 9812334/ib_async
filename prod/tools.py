import datetime
import socket
import datetime
import os
import pandas as pd
import platform
import chime
import os
import urllib

from config import *
from ib_async import *


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
            req = urllib.request.Request(f"{CHANIFY_URL}{CHANIFY_TOKEN}",
                data=data,
            )
            response = urllib.request.urlopen(req)
            response.read()  # Read the response to ensure the request is complete
        except urllib.error.URLError as e:
            print(f"Error sending request: {e.reason}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        
    return True


util.logToFile(f"{LOGS_DIR}/{datetime.datetime.now().strftime('%Y-%m-%d')}-{socket.gethostname()}.log")
util.startLoop()
util.logToConsole()

if "ib" in globals():
    ib.disconnect()


ib = IB()
ib.connect(IBKR_SERVER, IBKR_PORT, CLIENT_ID)


def ticker_contract_init(contract_id):

    contract = Contract(conId=contract_id)

    ib.qualifyContracts(contract)
    ticker = ib.reqMktDepth(contract=contract, isSmartDepth=True)

    ib.reqAccountSummary()  # run only once
    ib.reqAllOpenOrders()
    ib.reqPositions()

    return ticker, contract


def ticker_init(local_symbol):

    if local_symbol == "NQM2024":
        contract = Contract(conId=620730920)
    elif local_symbol == "NQU2024":
        contract = Contract(conId=637533450)
    else:
        raise Exception("Not implemented contract")

    ib.qualifyContracts(contract)
    ticker = ib.reqMktDepth(contract=contract, isSmartDepth=True)

    ib.reqAccountSummary()  # run only once
    ib.reqAllOpenOrders()
    ib.reqPositions()

    return ticker, contract

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


def print_account_summary(accounts=[IBKR_ACCOUNT_2, IBKR_ACCOUNT_1]):

    for account in accounts:
        print(f"Account: {account}")

        for item in ib.accountSummary(account=account):
            if item.tag in [
                "Account",
                "Cushion",
                "NetLiquidation",
                "GrossPositionValue"
                "TotalCashValue",
                "ExcessLiquidity",
                "BuyingPower",
                "LookAheadExcessLiquidity",
                "InitMarginReq",
                "MaintMarginReq",
            ]:
                print(item.tag, item.value)


def print_executions(cols = ["time", "side", "price", "permId", "shares"], tail = 5):
    executions_df = util.df(ib.executions())

    if executions_df is None:
        print(f"Executions: 0")
    else:
        print(f"Executions: {len(executions_df)}")

        if len(executions_df) > 0:
            print(executions_df[cols].tail(tail))

    return executions_df

def print_strategy_summary(strategy_details, open_trade, close_trade, ticker = None):
    print_clear()
    print(
        f"{strategy_details['strategy']} / {strategy_details['open_ticks']}:{strategy_details['close_ticks']} tickers / ({strategy_details['pause_replace']}_replace_sec)({strategy_details['pause_restart']}_restart_sec)"
    )
    print_line()

    if open_trade is not None:
        print_order(open_trade)
    else:
        print("Open Trade = None")
    print_line()

    if close_trade is not None:
        print_order(close_trade)
    else:
        print("Close Trade = None")
    print_line()

    print_line()
    print_orderbook(ticker=ticker)
    print_line()


def print_openOrders(cols = ["localSymbol", "permId", "action", "totalQuantity", "orderType", "lmtPrice", "tif", "status"]):

    open_orders_df = util.df(parse_ibrecords(ib.reqAllOpenOrders()))
    
    if open_orders_df is None:
        print(f"Open Orders: 0")
    else:
        print(f"Open Orders: {len(open_orders_df)}")

        print(open_orders_df[cols])

    return open_orders_df

def print_openTrades():
    open_trades = ib.openTrades()

    if open_trades is None or open_trades == []:
        print(f"Open Trades: 0")
        return None

    open_trades_df = util.df([t.order for t in open_trades]).loc[
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


def print_orderbook(ticker):
    if ticker is None:
        print(f"Orderbook: <TICKER NOT FOUND>")
        return None

    if ticker.domBids is not None and ticker.domAsks is not None:
        max_length = max(len(ticker.domBids), len(ticker.domAsks))

        sum_bid_size = sum([b.size for b in ticker.domBids])
        sum_ask_size = sum([a.size for a in ticker.domAsks])
        print(
            f"Orderbook: {ticker.contract.localSymbol} / {sum_bid_size} x | x {sum_ask_size}"
        )

        for i in range(max_length):
            bid_size = ticker.domBids[i].size if i < len(ticker.domBids) else "-"
            bid_price = ticker.domBids[i].price if i < len(ticker.domBids) else "-"
            ask_price = ticker.domAsks[i].price if i < len(ticker.domAsks) else "-"
            ask_size = ticker.domAsks[i].size if i < len(ticker.domAsks) else "-"
            print(f"{bid_size:>8} {bid_price:>10} | {ask_price:<10} {ask_size:<8}")

        # avg_bid_price = round(sum([b.price * b.size for b in ticker.domBids]) / sum_bid_size,1)
        # avg_ask_price = sum([b.price * b.size for b in ticker.domAsks]) / sum_ask_size


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
            f"{f.contract.localSymbol}\t{f.position} @ {round(f.avgCost/float(f.contract.multiplier or 1),3)}"
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

def test_tools(local_symbol, accounts = [IBKR_ACCOUNT_1], duration=5):
    ticker, contract = ticker_init(local_symbol=local_symbol)
    print_clear()
    print()
    print_orderbook(ticker=ticker)
    print_account_summary(accounts = accounts)
    print()
    print_executions()
    print()
    print_openOrders()
    print()
    print_openTrades()
    print()
    print_orderbook(ticker=ticker)
    print()
    print_positions()
    print()
    ib.disconnect()


def print_ibrecords(
    data_array,
    cols,
):
    df = util.df(data_array)
    df = df[cols]
    print(df)


if __name__ == "__main__":
    try:
        test_tools("NQU2024")

    except KeyboardInterrupt:
        ib.disconnect()

        print("Exiting...")
        exit(0)

    
