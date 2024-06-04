from tools import *


parser = argparse.ArgumentParser(description="IBKR Script")
parser.add_argument(
    "--dur",
    type=int,
    default=1,
    help="Duration for monitoring overview (in seconds)",
)
args = parser.parse_args()

def print_summary():
    executions = []
    positions = []
    open_orders = []
    
    while ib.sleep(duration):        
        print_clear()
        print(f"-" * 50)

        print_account_summary(accounts = ["U10394496"])
        print(f"-" * 50)

        current_executions = print_executions()
        print(f"-" * 50)

        if len(current_executions) != len(executions):
            alert()        

        current_open_orders = print_openOrders()
        print(f"-" * 50)

        current_positions = print_positions(contract=NQM4)
        print(f"-" * 50)
        
        print_orderbook()
        print(f"-" * 50)

        executions = current_executions
        open_orders = current_open_orders
        positions = current_positions

def onTickerUpdate(ticker):
    print(f"-" * 50)

    print_account_summary(accounts = ["U10394496"])
    print(f"-" * 50)

    current_executions = print_executions()
    print(f"-" * 50)

    current_open_orders = print_openOrders()
    print(f"-" * 50)

    current_positions = print_positions(contract=NQM4)
    print(f"-" * 50)
    
    print_orderbook()
    print(f"-" * 50)


if __name__ == "__main__":
    
    ib, ticker, NQM4 = init()

    print(args)

    executions = []
    open_orders = []
    positions = []

    ticker.updateEvent += onTickerUpdate

    while ib.sleep(1):
        if len(current_executions) != len(executions):
            alert(True)

        executions = current_executions
        open_orders = current_open_orders
        positions = current_positions
