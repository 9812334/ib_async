import datetime
import random
import os
import pandas as pd
import socket
import time

from ib_async import *

hostname = socket.gethostname()
util.logToFile(f"{datetime.datetime.now().strftime('%Y-%m-%d')}-{hostname}.log")
util.startLoop()
util.logToConsole()

if "ib" in globals():
    ib.disconnect()

randint = lambda a=1, b=10: random.randint(a, b)
ib = IB()
ib.connect("127.0.0.1", 4001, randint(1, 99))

# from supabase import create_client, Client
# connect to supabase server
# url: str = "https://dbcizmxdlufqncxipqwt.supabase.co"
# key: str = (
#     "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRiY2l6bXhkbHVmcW5jeGlwcXd0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDE4NDkxMTMsImV4cCI6MjAxNzQyNTExM30.ys98bhleekrfDJAbrMMqXGsVh1XMa3Vtl8O62s7D5as"
# )
# supabase: Client = create_client(url, key)


import platform
import chime


def chime_success():
    if platform.system() == "Linux":
        chime.success()
    elif platform.system() == "Darwin":
        os.system("say beep")
    elif platform.system() == "Windows":
        raise Exception("not handled yet")


import urllib


def push_notifications(msg="Hello world!"):
    try:
        body = f"[{datetime.datetime.now()}] {msg}"
        print(body)
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


def print_reqOpenOrders():
    print("Session Orders::")
    display(util.df([t.order for t in ib.reqOpenOrders()]))


def print_reqAllOpenOrders():
    print("All Session Orders:")
    display(util.df([t.order for t in ib.reqAllOpenOrders()]))


def print_account_summary(ib):
    print("ACCOUNT SUMMARY::\n")
    acct_fields = ib.accountSummary(account="U10394496")

    for f in acct_fields:
        if "DayTrades" not in f.tag:
            print(f.tag, ":", f.value)
    print()


def print_order(o):
    if o is None:
        print()
        return

    order = o.order
    contract = o.contract
    orderStatus = o.orderStatus

    # print(f"symbol\tpermId\t\tstatus\t\taction\tfilled\tremaining\tlmtPrice")

    print(
        f"Order # {contract.symbol}\t{order.permId}\t{orderStatus.status}\t\t{order.action}\t{orderStatus.filled}\t{orderStatus.remaining}\t\t{order.lmtPrice}\t"
    )


def print_executions():
    fills = [t.fills for t in ib.trades() if t.fills != []]
    executions = [f[0].execution for f in fills]
    print(f"Intraday Executions: {len(executions)}\n")


def print_positions():
    print("POSITIONS::")
    future = [pos for pos in ib.positions()]
    for f in future:
        print(
            f"{f.contract.symbol} {f.position} @ {f.avgCost/float(contract.multiplier)}"
        )
    print()


def print_openOrders(status_list=["Submitted", "PendingSubmit", "PendingCancel"]):
    print(":: openOrders ::")
    display(util.df([t for t in ib.openOrders()]))


def print_submittedtrades():
    print(":: trades ::")
    display(
        util.df(
            [
                t.order
                for t in ib.trades()
                if t.orderStatus.status == "Submitted"
                or t.orderStatus.status == "PreSubmitted"
                or t.orderStatus.status == "PendingSubmit"
            ]
        )
    )


# NQM2024 contract
print("Setting contract to NQM2024 symbol / JUN 2024 / Contract(conId=620730920)")
contract = Contract(conId=620730920)
ib.qualifyContracts(contract)

ticker = ib.reqMktDepth(contract)

ib.sleep(5)


def print_orderbook():
    print("NQ Order Book::")
    if ticker is not None and ticker.domBids is not None and ticker.domAsks is not None:
        for i in range(min(len(ticker.domBids), len(ticker.domAsks))):
            bid_size = ticker.domBids[i].size
            bid_price = ticker.domBids[i].price
            ask_price = ticker.domAsks[i].price
            ask_size = ticker.domAsks[i].size
            print(f"{bid_size:>8} {bid_price:>10} | {ask_price:<10} {ask_size:<8}")
    print()


print_orderbook()


def run_strategy(strategy_details, open_permId, close_permId, cancel_permids=[]):
    open_trade = None
    close_trade = None
    open_order = None
    close_order = None
    open_order_ts = None

    push_notifications(
        f"-------- {strategy_details} / {open_permId} / {close_permId} / {cancel_permids}"
    )

    if open_permId is not None:
        orders = [t.order for t in ib.reqAllOpenOrders()]
        for o in orders:
            if o.permId == open_permId:
                open_order = o

    if open_order is not None:
        push_notifications(f"OPEN ORDER:: {open_order}")

    if open_trade is None:
        trades = ib.trades()
        for o in trades:
            if o.orderStatus.permId == open_permId:
                open_trade = o

    # push_msg(f"OPEN TRADE:: {open_trade.order}")

    if close_permId is not None:
        for o in orders:
            if o.permId == close_permId:
                close_order = o

    if close_order is not None:
        push_notifications(f"CLOSE ORDER:: {close_order}")

    if close_trade is None:
        trades = ib.trades()
        for o in trades:
            if o.orderStatus.permId == close_permId:
                close_trade = o

    # print(f"CLOSE TRADE:: {close_trade}")

    for permId in cancel_permids:
        cancelled_order = None
        for o in orders:
            if o.permId == permId:
                print("Cancelling order.permId {o.permId}")
                cancelled_order = ib.cancelOrder(o)
                ib.sleep(2)
                if cancelled_order.orderStatus.status == "Cancelled":
                    print(f"Order {o.permId} has been cancelled")
                else:
                    raise Exception("Unable to cancel order {o.permId}")

        if cancelled_order is None:
            raise Exception(":: ORDER TO CANCEL NOT FOUND ::  {permId}")

    pause = False
    ib.sleep(1)

    while True:

        print(
            f"-------- {strategy_details} / open {open_permId} / close {close_permId} / cancels {cancel_permids}"
        )

        # first order of the strategy
        if open_trade is None and close_trade is None:
            action = strategy_details["open_action"]
            qty = strategy_details["open_qty"]

            if ticker is None or len(ticker.domBids) == 0 or len(ticker.domAsks) == 0:
                print("************ Issue getting orderbok *************** ")
                ib.sleep(1)
                continue

            if strategy_details["open_ref"] == "bid":
                price_ref = ticker.domBids[0].price
            elif strategy_details["open_ref"] == "ask":
                price_ref = ticker.domAsks[0].price
            elif strategy_details["open_ref"] == "mid":
                price_ref = (ticker.domAsks[0].price + ticker.domBids[0].price) / 2
            elif strategy_details["open_ref"] == "last":
                raise Exception("Not implemented")

            lmtPrice = (
                price_ref
                + strategy_details["open_ticks"] * strategy_details["tick_increment"]
            )
            print(
                f"Placing open trade: {action}, {strategy_details['open_type']}, totalQuantity {qty}, lmtPrice {lmtPrice}"
            )

            if strategy_details["open_type"] == "LIMIT":
                open_order = LimitOrder(
                    action=action,
                    totalQuantity=qty,
                    lmtPrice=lmtPrice,
                    account="U10394496",
                )
            else:
                raise Exception("Not implemented")

            open_trade = ib.placeOrder(contract, open_order)
            trade = open_trade

            push_notifications(
                f"OPEN ORDER PLACED :: #{trade.order.permId} {trade.orderStatus.status} {trade.contract.symbol} {trade.order.action} {trade.orderStatus.filled}/{trade.orderStatus.remaining} @ {trade.order.lmtPrice}"
            )

            open_order_ts = datetime.datetime.now()

        print_order(open_trade)
        print(
            "--------------------------------------------------------------------------------------"
        )

        if open_trade is not None:
            if open_trade.orderStatus.status == "Submitted" and close_trade is None:
                print(
                    f"Waiting to get filled on order #{open_trade.order.permId} ({open_trade.orderStatus.status})"
                )

                if (
                    open_order_ts is None
                    or datetime.datetime.now() - open_order_ts
                    > datetime.timedelta(seconds=strategy_details["pause_seconds"])
                ):
                    print("Cancelling order due to timeout:")
                    ib.cancelOrder(open_trade.order)

            if open_trade.orderStatus.status == "Filled" and close_trade is None:
                print(
                    "Filled on open_trade {open_trade.orderStatus.status} {open_trade.orderStatus.avgFillPrice} {open_trade.orderStatus.status}"
                )

                action = strategy_details["close_action"]
                qty = strategy_details["close_qty"]

                if strategy_details["close_ref"] == "open_price_fill":
                    price_ref = open_trade.orderStatus.avgFillPrice
                if strategy_details["close_ref"] == "bid":
                    price_ref = ticker.domBids[0].price
                elif strategy_details["close_ref"] == "ask":
                    price_ref = ticker.domAsks[0].price
                elif strategy_details["close_ref"] == "mid":
                    price_ref = (ticker.domAsks[0].price + ticker.domBids[0].price) / 2
                elif strategy_details["close_ref"] == "last":
                    raise Exception("Not implemented")

                lmtPrice = (
                    price_ref
                    + strategy_details["close_ticks"]
                    * strategy_details["tick_increment"]
                )

                if strategy_details["close_type"] == "LIMIT":
                    close_order = LimitOrder(
                        action=action,
                        totalQuantity=qty,
                        lmtPrice=lmtPrice,
                        account="U10394496",
                    )
                else:
                    raise Exception("Not implemented")

                close_trade = ib.placeOrder(contract, close_order)

                # chime.info()
                push_notifications(msg=f"OPEN ORDER FILLED:: {open_trade.order}")
                push_notifications(msg=f"CLOSE ORDER PLACED:: {close_trade.order}")

            elif (
                open_trade.orderStatus.status == "Inactive"
                or open_trade.orderStatus.status == "Cancelled"
            ) and close_trade is None:
                # push_notifications(f"OPEN TRADE CANCELLED:: {open_trade.order}")
                open_trade = None

        print_order(close_trade)
        print(
            "--------------------------------------------------------------------------------------"
        )

        if close_trade is not None:
            if close_trade.orderStatus.status == "Filled":
                print(
                    "Close trade filled @ {}".format(
                        close_trade.orderStatus.avgFillPrice
                    )
                )
                os.system("say beep")
                chime_success()
                push_notifications(f"CLOSE TRADE FILLED:: {close_trade.order}")
                open_trade = None
                close_trade = None
                pause = True

                print(
                    "--------------------------------------------------------------------------------------"
                )

        if (
            ticker is not None
            and ticker.domBids is not None
            and ticker.domAsks is not None
        ):
            max_length = max(len(ticker.domBids), len(ticker.domAsks))
            for i in range(max_length):
                bid_size = ticker.domBids[i].size if i < len(ticker.domBids) else "-"
                bid_price = ticker.domBids[i].price if i < len(ticker.domBids) else "-"
                ask_price = ticker.domAsks[i].price if i < len(ticker.domAsks) else "-"
                ask_size = ticker.domAsks[i].size if i < len(ticker.domAsks) else "-"
                print(f"{bid_size:>8} {bid_price:>10} | {ask_price:<10} {ask_size:<8}")

        print(
            "--------------------------------------------------------------------------------------"
        )
        future = [pos for pos in ib.positions() if pos.contract.secType == "FUT"]
        for f in future:
            print(
                f"{f.contract.symbol} {f.position} @ {f.avgCost/float(contract.multiplier)} ({len(ib.executions())} executions)"
            )
        print(
            "--------------------------------------------------------------------------------------"
        )

        print(
            util.df(ib.openOrders())
            .sort_values("lmtPrice", ascending=False)
            .loc[
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
        )

        # openOrders = parse_ibrecords(ib.openOrders())
        # print_ibrecords_table(
        #     openOrders,
        #     cols=[
        #         "localSymbol",
        #         "permId",
        #         "status",
        #         "orderType",
        #         "action",
        #         "lmtPrice",
        #         "remaining",
        #     ],
        # )

        print()
        print("------- U10394496 ----------")

        for item in ib.accountSummary(account="U10394496"):
            if item.tag in [
                "Account",
                "Cushion",
                "NetLiquidation",
                "TotalCashValue",
                "LookAheadExcessLiquidity",
            ]:
                print(item.tag, item.value)

        print("------- U2340948 ----------")

        for item in ib.accountSummary(account="U2340948"):
            if item.tag in [
                "Account",
                "Cushion",
                "NetLiquidation",
                "FullExcessLiquidity",
                "LookAheadExcessLiquidity",
            ]:
                print(item.tag, item.value)

        if pause:
            open_orders = ib.reqAllOpenOrders()
            executions = ib.reqExecutions()

            ib.sleep(strategy_details["pause_seconds"])
            pause = False
        else:
            ib.sleep(1)

        os.system("cls" if os.name == "nt" else "clear")


sell_scalp = {
    "strategy": "SELL TO OPEN SCALP",
    "contract": "NQM2024",
    "tick_increment": 0.25,
    "open_qty": 1,
    "open_type": "LIMIT",
    "open_action": "SELL",
    "open_ref": "ask",
    "open_ticks": 10,
    "close_qty": 1,
    "close_type": "LIMIT",
    "close_action": "BUY",
    "close_ref": "open_price_fill",
    "close_ticks": -10,
    "pause_seconds": 90,
}

buy_scalp = {
    "strategy": "BUY TO OPEN SCALP",
    "contract": "NQM2024",
    "tick_increment": 0.25,
    "open_qty": 1,
    "open_type": "LIMIT",
    "open_action": "BUY",
    "open_ref": "ask",
    "open_ticks": -5,
    "close_qty": 1,
    "close_type": "LIMIT",
    "close_action": "SELL",
    "close_ref": "open_price_fill",
    "close_ticks": 10,
    "pause_seconds": 70,
}


run_strategy(
    strategy_details=buy_scalp,
    open_permId=527389862,
    close_permId=527389863,
    cancel_permids=[],
)
