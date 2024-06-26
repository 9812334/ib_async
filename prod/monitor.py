from tools import *

import argparse
import random

parser = argparse.ArgumentParser(description="IBKR Script")
parser.add_argument(
    "--dur",
    type=int,
    default=1,
    help="Duration for monitoring overview (in seconds)",
)

args = parser.parse_args()


def monitor_overview(local_symbol, accounts = [IBKR_ACCOUNT_1], duration=5):
    executions = []
    positions = []
    open_orders = []

    ticker, contract = ticker_init(local_symbol= local_symbol)

    while ib.sleep(duration):        
        print_clear()
        print(f"-" * 50)

        print_account_summary(accounts = accounts)
        print(f"-" * 50)

        current_executions = print_executions()
        print(f"-" * 50)

        if current_executions is not None and executions is not None and len(current_executions) != len(executions):
            alert()

        current_open_orders = print_openOrders()
        print(f"-" * 50)

        current_positions = print_positions(contract=contract)
        print(f"-" * 50)

        print_orderbook(ticker=ticker)
        print(f"-" * 50)

        executions = current_executions
        open_orders = current_open_orders
        positions = current_positions

        if random.randint(0,5) == 3:
            ib.reqExecutions()

if __name__ == "__main__":
    try:
        monitor_overview(local_symbol="NQU2024", duration=5)
    except KeyboardInterrupt:
        print("Interrupted by user")

    ib.disconnect()
    exit(0)
