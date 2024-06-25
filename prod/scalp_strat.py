from strat import *

import argparse


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='My Python Script')
    parser.add_argument('--strat', type=str, help='Strategy', default='')
    parser.add_argument('--open_id', type=int, help='Open ID', default=0)
    parser.add_argument('--close_id', type=int, help='Close ID', default=0)
    parser.add_argument('--cancel_id', type=int, help='Cancel ID', default=0)
    parser.add_argument("--open_ticks", type=int, help="Open Ticks", default=-1)
    parser.add_argument("--close_ticks", type=int, help="Close Ticks", default=-1)

    args = parser.parse_args()

    print(f'Strategy: {args.strat}')
    print(f'OPEN ID: {args.open_id}')
    print(f'CLOSE ID: {args.close_id}')
    print(f'CANCEL ID: {args.cancel_id}')

    if args.strat == "buy" or args.strat == "BUY_SCALP":
        STRATEGY = BUY_SCALP
    elif args.strat == "sell" or args.strat == "SELL_SCALP":
        STRATEGY = SELL_SCALP
    else:
        print("Invalid strategy")
        ib.disconnect()
        exit(0)

    STRATEGY["push"] = True
    STRATEGY["live"] = True
    STRATEGY["debug"] = False
    STRATEGY["open_permid"] = args.open_id
    STRATEGY["close_permid"] = args.close_id
    STRATEGY["cancel_permid"] = args.cancel_id

    if args.open_ticks != -1:
        STRATEGY["open_ticks"] = int(args.open_ticks)

    if args.close_ticks != -1:
        STRATEGY["close_ticks"] = args.close_ticks

    try:
        pprint.pprint(f"STRATEGY: \n {STRATEGY}")
        simple_scalp(STRATEGY)

    except KeyboardInterrupt:
        print('Interrupted')

    ib.disconnect()
    exit(0)