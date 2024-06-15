from strat import *

SELL_SCALP = {
    "strategy": "SELL TO OPEN SCALP",
    "contract": "NQM2024",
    "tick_increment": 0.25,
    "open_qty": 1,
    "open_type": "LIMIT",
    "open_action": "SELL",
    "open_ref": "ask",
    "open_ticks": 15,
    "close_qty": 1,
    "close_type": "LIMIT",
    "close_action": "BUY",
    "close_ref": "open_fill",
    "close_ticks": -10,
    "pause_seconds": 60,
}

BUY_SCALP = {
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
    "close_ref": "open_fill",
    "close_ticks": 10,
    "pause_seconds": 10,
}


DEBUG = False
LIVE = True

if __name__ == "__main__":
    open_permid = None # get_last_trade_permid(n=0)
    close_permid = None # get_last_trade_permid()
    print(open_permid, ";", close_permid)

    run_ss_2(strategy_details=BUY_SCALP, open_permid=open_permid, close_permid = close_permid, push = True)
