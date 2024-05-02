import os

if os.name != "posix":
    import winsound


def play_beep(freq=2500, dur=500):
    # On Mac, use the "afplay" command to play a beep sound
    if os.name == "posix":
        os.system("afplay /System/Library/Sounds/Glass.aiff")
    else:
        winsound.Beep(2500, 500)


play_beep(500, 500)


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

    trades = ib.reqOpenOreders()

    trades.sort(key=lambda trade: trade.order.lmtPrice)

    for trade in trades:
        orderstatus = trade.orderStatus
        order = trade.order

        if trade.contract.symbol != sym:
            continue

        print(
            f"{trade.contract.symbol}\t{order.permId}\t{orderstatus.status}\t{order.action}\t{orderstatus.filled}\t{orderstatus.remaining}\t\t{order.lmtPrice}\t"
        )


def print_openorders(ib):
    orders = ib.openOrders()
    orders.sort(key=lambda order: order.lmtPrice)

    # Order(orderId=658, clientId=3124, permId=342738244, action='SELL', totalQuantity=1.0, orderType='LMT', lmtPrice=17692.5, auxPrice=0.0, tif='GTC', ocaType=3, displaySize=2147483647, rule80A='0', openClose='', volatilityType=0, deltaNeutralOrderType='None', referencePriceType=0, account='U10394496', clearingIntent='IB', adjustedOrderType='None', cashQty=0.0, dontUseAutoPriceForHedge=True)

    for order in orders:
        print(
            f"{order.permId}\t{order.action}\t{order.totalQuantity}\t{order.lmtPrice}\t{order.tif}"
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
