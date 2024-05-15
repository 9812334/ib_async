import os
import os
from supabase import create_client, Client

url: str = "https://dbcizmxdlufqncxipqwt.supabase.co"
key: str = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRiY2l6bXhkbHVmcW5jeGlwcXd0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDE4NDkxMTMsImV4cCI6MjAxNzQyNTExM30.ys98bhleekrfDJAbrMMqXGsVh1XMa3Vtl8O62s7D5as"
)
supabase: Client = create_client(url, key)


if os.name != "posix":
    import winsound


def play_beep(freq=2500, dur=500):
    # On Mac, use the "afplay" command to play a beep sound
    if os.name == "posix":
        os.system("afplay /System/Library/Sounds/Glass.aiff")
    else:
        winsound.Beep(2500, 500)


def import_trades(trades):
    for t in trades:
        print(t)
        d = {
            "contract_sectype": t.contract.secType,
            "contract_conid": int(t.contract.conId),
            "contract_symbol": t.contract.symbol,
            "contract_lasttradedateorcontractmonth": t.contract.lastTradeDateOrContractMonth,
            "contract_multiplier": int("1" or t.contract.multiplier),
            "contract_currency": t.contract.currency,
            "contract_localsymbol": t.contract.localSymbol,
            "contract_tradingclass": t.contract.tradingClass,
            "order_permid": int(t.order.permId),
            "order_action": t.order.action,
            "order_ordertype": t.order.orderType,
            "order_lmtprice": float(t.order.lmtPrice),
            "order_tif": t.order.tif,
            "order_ocatype": t.order.ocaType,
            "order_account": t.order.account,
            "order_autocanceldate": t.order.autoCancelDate,
            "order_filledquantity": float(t.order.filledQuantity),
            "order_reffuturesconid": int(t.order.refFuturesConId),
            "orderstatus": t.orderStatus.status,
        }

        data, count = supabase.table("trades").upsert(d).execute()

    print(f"Imported {len(trades)} trades")


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


def print_account_summary(ib):
    acct_fields = ib.accountSummary(account="U10394496")

    for f in acct_fields:
        if "DayTrades" not in f.tag:
            print(f.tag, ":", f.value)


def print_trades(ib, trades):

    trades.sort(key=lambda trade: trade.order.lmtPrice)

    for trade in trades:
        orderstatus = trade.orderStatus
        order = trade.order

        print(
            f"{trade.contract.symbol}\t{order.permId}\t{orderstatus.status}\t\t{order.action}\t{orderstatus.filled}\t{orderstatus.remaining}\t\t{order.lmtPrice}\t"
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


def push_msg():
    print()
