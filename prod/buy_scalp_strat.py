from strat import *

DEBUG = False
LIVE = True
STRATEGY = BUY_SCALP
PUSH = False
OPEN_PERMID = None
CLOSE_PERMID = None
CANCEL_PERMID = None

if __name__ == "__main__":

    STRATEGY["push"] = PUSH
    STRATEGY["open_permid"] = OPEN_PERMID
    STRATEGY["close_permid"] = CLOSE_PERMID
    STRATEGY["cancel_permid"] = CANCEL_PERMID
    STRATEGY["live"] = LIVE
    STRATEGY["debug"] = DEBUG

    try:
        simple_scalp(STRATEGY)

    except KeyboardInterrupt:
        ib.disconnect()
        exit(0)
