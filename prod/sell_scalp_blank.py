from strat import *

DEBUG = False
LIVE = True

if __name__ == "__main__":
    open_permid = None # get_last_trade_permid(n=0)
    close_permid = None # get_last_trade_permid()
    print(open_permid, ";", close_permid)

    run_ss_2(strategy_details=SELL_SCALP, open_permid=open_permid, close_permid = close_permid, push = True)
