from tools import *

parser = argparse.ArgumentParser(description="IBKR Script")
parser.add_argument(
    "--dur",
    type=int,
    default=1,
    help="Duration for monitoring overview (in seconds)",
)
parser.add_argument(
    "--strat",
    type=str,
    choices=["ss_buy", "ss_sell", "monitor"],
    help="Strategy details: 1) ss_buy, 2) ss_sell, 3) monitor",
)
parser.add_argument(
    "--open",
    type=int,
    help="Open permId",
    default=None
)
parser.add_argument(
    "--close",
    type=int,
    help="Close permId",
    default=None,
)
args = parser.parse_args()


def monitor_overview(local_symbol, accounts = ["U10394496"], duration=5):
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

        # if len(current_executions) != len(executions):
        #     alert()

        current_open_orders = print_openOrders()

        if len(current_open_orders) != len(open_orders):
            ib.reqExecutions()

        print(f"-" * 50)

        current_positions = print_positions(contract=contract)
        print(f"-" * 50)

        print_orderbook(ticker=ticker)
        print(f"-" * 50)

        executions = current_executions
        open_orders = current_open_orders
        positions = current_positions


if __name__ == "__main__":
    print(args)
    monitor_overview(local_symbol="NQU2024", duration=args.dur)
