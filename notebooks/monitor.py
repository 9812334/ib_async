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



if __name__ == "__main__":
    print(args)
    # ticker = ticker_init()
    monitor_overview(duration=args.dur)
