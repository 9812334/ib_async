from IPython.core.display import HTML
from IPython.display import display, clear_output

display(HTML("<style>.output_subarea { overflow: auto; }</style>"))

import datetime
import random
import os
import pandas as pd
import socket

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

    print(f"symbol\tpermId\t\tstatus\t\taction\tfilled\tremaining\tlmtPrice")

    print(
        f"{contract.symbol}\t{order.permId}\t{orderStatus.status}\t{order.action}\t{orderStatus.filled}\t{orderStatus.remaining}\t\t{order.lmtPrice}\t"
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
