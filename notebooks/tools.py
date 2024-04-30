import os
import winsound


def play_beep():
    # On Mac, use the "afplay" command to play a beep sound
    if os.name == 'posix':
        os.system('afplay /System/Library/Sounds/Glass.aiff')
    else:
        winsound.Beep(2500, 500)
        
    
def get_all_openorders(ib, sym="NQ"):
    trades = ib.reqAllOpenOrders()
    trades.sort(key=lambda trade: trade.order.lmtPrice)

    trades = [trade for trade in trades if trade.contract.symbol == sym]
    return trades


def print_cancelled_orders(ib):
    # canceled orders
    print(f"permId\t\taction\t\ttotalQuantity\tfilledQuantity\t\tlmtPrice")

    closedOrders = ib.orders()
    [
        print(
            f"{order.permId}\t{order.action}\t\t{order.totalQuantity}\t\t{order.filledQuantity}\t\t\t{order.lmtPrice}"
        )
        for order in closedOrders
        if order.filledQuantity == 0
    ]

def print_all_openorders(ib, sym="NQ"):
    print(f"symbol\tpermId\t\tstatus\t\taction\tfilled\tremaining\tlmtPrice")

    trades = ib.reqAllOpenOrders()

    trades.sort(key=lambda trade: trade.order.lmtPrice)

    for trade in trades:
        orderstatus = trade.orderStatus
        order = trade.order

        if trade.contract.symbol != sym:
            continue

        print(
            f"{trade.contract.symbol}\t{order.permId}\t{orderstatus.status}\t{order.action}\t{orderstatus.filled}\t{orderstatus.remaining}\t\t{order.lmtPrice}\t"
        )


def print_account_summary(ib):
    acct_fields = ib.accountSummary(account="U10394496")

    for f in acct_fields:
        if "DayTrades" not in f.tag:
            print(f.tag, ":", f.value)
            
def print_trades(ib, trades):
    print(f"symbol\tpermId\t\tstatus\t\taction\tfilled\tremaining\tlmtPrice")

    trades.sort(key=lambda trade: trade.order.lmtPrice)

    for trade in trades:
        orderstatus = trade.orderStatus
        order = trade.order

        print(
            f"{trade.contract.symbol}\t{order.permId}\t{orderstatus.status}\t{order.action}\t{orderstatus.filled}\t{orderstatus.remaining}\t\t{order.lmtPrice}\t"
        )

def print_order(o):
    if o is None:
        print(o)
        return

    order = o.order
    contract = o.contract
    orderStatus = o.orderStatus

    print(f"symbol\tpermId\t\tstatus\t\taction\tfilled\tremaining\tlmtPrice")

    print(
        f"{contract.symbol}\t{order.permId}\t{orderStatus.status}\t{order.action}\t{orderStatus.filled}\t{orderStatus.remaining}\t\t{order.lmtPrice}\t"
    )
