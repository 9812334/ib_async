from tools import *

import argparse
import random

parser = argparse.ArgumentParser(description="IBKR Monitor Script")
parser.add_argument(
    "--dur",
    type=int,
    default=1,
    help="Duration for monitoring overview (in seconds)",
)

args = parser.parse_args()

import datetime

def monitor_overview(local_symbol, accounts = [IBKR_ACCOUNT_1], duration=5):
    executions = []
    positions = []
    previous_orders = []

    ticker, contract = ticker_init(local_symbol= local_symbol)

    # every 5 seconds reqExecutions()
    t1 = datetime.datetime.now().timestamp()
    now = datetime.datetime.now().timestamp()

    while ib.sleep(1):
        current_orders = util.df(parse_ibrecords(ib.reqAllOpenOrders()))

        if len(previous_orders) != len(current_orders):
            alert()
            ib.reqPositions()

        print_clear()
        # now = datetime.datetime.now().timestamp()
        # if now - t1 > datetime.timedelta(seconds=duration).total_seconds():
        #     print(f"Time elapsed: {now - t1}")
        #     ib.reqPositions()
        #     ib.reqAllOpenOrders()
        #     t1 = datetime.datetime.now().timestamp()

        print_account_summary(accounts=accounts)
        print(f"-" * 50)

        print_trades(status = 'Filled', tail = 15)
        print(f"-" * 50)
        
        print_trades(status="Submitted", tail=15)
        print(f"-" * 50)
        
        # current_executions = print_executions(tail = 6)
        # print(f"-" * 50)

        current_positions = print_positions(contract=contract)
        print(f"-" * 50)

        print_orderbook(ticker=ticker)
        print(f"-" * 50)

        # executions = current_executions
        previous_orders = current_orders
        positions = current_positions


if __name__ == "__main__":
    try:
        monitor_overview(local_symbol="NQU2024", duration=5)
    except KeyboardInterrupt:
        print("Interrupted by user")

    ib.disconnect()
    exit(0)
