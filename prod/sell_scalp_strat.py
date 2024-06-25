from strat import *


DEBUG = False
LIVE = True
STRATEGY = SELL_SCALP
PUSH = False

if __name__ == "__main__":

    STRATEGY["push"] = PUSH
    STRATEGY["live"] = LIVE
    STRATEGY["debug"] = DEBUG

    try:
        simple_scalp(STRATEGY)

    except KeyboardInterrupt:
        print('Interrupted')
        
    ib.disconnect()
    exit(0)
