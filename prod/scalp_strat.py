from tools import *


BUY_SCALP = {
    "margin_cushion_pct": 5,
    "account": IBKR_ACCOUNT_1,
    "strategy": "BUY TO OPEN SCALP",
    "contract": "NQU2024",
    "contract_id": None,
    "tick_increment": 0.25,
    "open_qty": 1,
    "open_type": "LIMIT",
    "open_action": "BUY",
    "open_ref": "bid",
    "close_qty": 1,
    "close_type": "LIMIT",
    "close_action": "SELL",
    "close_ref": "open_fill",
    "open_ticks": -4,
    "close_ticks": 10,
}

SELL_SCALP = {
    "margin_cushion_pct": 0,
    "account": IBKR_ACCOUNT_1,
    "strategy": "SELL TO OPEN SCALP",
    "contract": "NQU2024",
    "contract_id": 637533450,
    "tick_increment": 0.25,
    "open_qty": 1,
    "open_type": "LIMIT",
    "open_action": "SELL",
    "open_ref": "ask",
    "open_ticks": 5,
    "close_ticks": -10,
    "close_qty": 1,
    "close_type": "LIMIT",
    "close_action": "BUY",
    "close_ref": "open_fill",
    "open_permid": None,
    "close_permid": None,
    "cancel_permid": None
}


def refresh():
    ib.reqAllOpenOrders()
    ib.reqPositions()


def simple_scalp(strat):

    def get_open_close_trades(open_permid, close_permid, push):
        open_trade = get_trade_by_permid(open_permid)
        close_trade = get_trade_by_permid(close_permid)

        if open_trade is not None:
            push_notifications(
                f"OPEN TRADE:: #{open_trade.order.permId} {open_trade.order.action} {open_trade.contract.localSymbol} {open_trade.order.orderType} @{open_trade.order.lmtPrice} filled {open_trade.order.filledQuantity}'",
                push,
            )

        if close_trade is not None:
            push_notifications(
                f"CLOSE TRADE:: #{close_trade.order.permId} {close_trade.order.action} {close_trade.contract.localSymbol} {close_trade.order.orderType} @{close_trade.order.lmtPrice} filled {close_trade.order.filledQuantity}'",
                push,
            )

        return open_trade, close_trade

    local_symbol = strat["contract"]

    ticker, contract = ticker_init(local_symbol=local_symbol)

    push_notifications(
        f"{strat['strategy']} / {strat['open_ticks']}:{strat['close_ticks']} tickers / ({strat['pause_replace']}_replace_sec)({strat['pause_restart']}_restart_sec)"
    )

    open_trade, close_trade = get_open_close_trades(
        strat["open_permid"], strat["close_permid"], strat["push"]
    )

    close_order_timestamp = None
    open_order_timestamp = None

    if strat["debug"]:
        proceed = input("Proceed? ")

        if proceed.lower() != "y":
            exit()

    while ib.waitOnUpdate():

        print_strategy_summary(strat, open_trade, close_trade, ticker)

        # if open_trade.orderStatus.status == 'PendingSubmit':
        #     print(f"Waiting for pending open_trade to be canceled...")
        #     cxl_order = ib.cancelOrder(open_trade.order)
        #     continue

        if close_order_timestamp is not None and (
            datetime.datetime.now() - close_order_timestamp
            < datetime.timedelta(seconds=strat["pause_restart"])
        ):
            print(
                f'Waiting {strat["pause_restart"] - (datetime.datetime.now() - close_order_timestamp).seconds} seconds...'
            )
            continue

        # execution part - first order of the strategy
        if open_trade is None and close_trade is None:
            action = strat["open_action"]
            qty = strat["open_qty"]

            if ticker is None or len(ticker.domBids) == 0 or len(ticker.domAsks) == 0:
                print(f"************ Issue getting orderbook tickers *************** ")
                alert(True)
                ib.waitOnUpdate()
                continue

            if strat["open_ref"] == "bid":
                price_ref = ticker.domBids[0].price
            elif strat["open_ref"] == "ask":
                price_ref = ticker.domAsks[0].price
            elif strat["open_ref"] == "mid":
                price_ref = (ticker.domAsks[0].price + ticker.domBids[0].price) / 2
            else:
                raise Exception("Not implemented")

            limit_price = price_ref + strat["open_ticks"] * strat["tick_increment"]

            if strat["open_type"] == "LIMIT":
                open_order = LimitOrder(
                    action=action,
                    totalQuantity=qty,
                    lmtPrice=limit_price,
                    account=strat["account"],
                )
            else:
                raise Exception("Not implemented")

            print(f"Pre-submitting order for open_trade {open_order} ")

            open_order_state = ib.whatIfOrder(contract, open_order)

            print(f"Order state: {open_order_state}")

            if open_order_state is None:
                raise Exception(
                    f"************ Issue placing whatIfOrder *************** "
                )
                alert(True)
                ib.waitOnUpdate()
                continue
            else:
                accountSummary = util.df(ib.accountSummary(account=strat["account"]))

                net_liquidation_value = float(
                    accountSummary[accountSummary["tag"] == "NetLiquidation"]["value"]
                )

                cushion = net_liquidation_value * strat["margin_cushion_pct"] / 100

                if net_liquidation_value - cushion > float(
                    open_order_state.initMarginAfter
                ) and net_liquidation_value - cushion > float(
                    open_order_state.maintMarginAfter
                ):

                    if strat["live"]:
                        open_trade = ib.placeOrder(contract, open_order)
                        ib.sleep(0.1)
                        open_order_timestamp = datetime.datetime.now()

                        trade = open_trade

                        push_notifications(
                            f"OPEN ORDER PLACED :: #{trade.order.permId} {trade.orderStatus.status} {trade.contract.symbol} {trade.order.action} {trade.orderStatus.filled}/{trade.orderStatus.remaining} @ {trade.order.lmtPrice}",
                            strat["open_push"],
                        )

                    else:
                        # TODO: you can mock trades here
                        print(f"[NOT LIVE] OPEN ORDER PLACED :: {open_order}")
                else:
                    print(
                        f"************ Failed Margin Check: Net Liq Value {net_liquidation_value} - {cushion} cushion < (initMarginAfter {open_order_state.initMarginAfter} | maintMarginAfter {open_order_state.maintMarginAfter}) *************** "
                    )

                    # ib.cancelOrder(open_order)

                    if strat['margin_check']:
                        alert(False)
                        ib.sleep(25)
                        continue
                    

        if open_trade is not None:
            if (
                open_trade.orderStatus.status == "Inactive"
                or open_trade.orderStatus.status == "Cancelled"
            ):
                print(
                    f"OPEN TRADE STATUS CANCELLED:: {open_trade.order}",
                    strat["open_push"],
                )

                for trade_entry in open_trade.log:
                    if trade_entry.status == "Cancelled":
                        push_notifications(f"{trade_entry}", strat["open_push"])
                open_trade = None

            elif open_trade.orderStatus.status == "Submitted" and close_trade is None:
                print(
                    f"Waiting to get filled on order #{open_trade.order.permId} ({open_trade.orderStatus.status})"
                )

                if (
                    open_order_timestamp is None
                    or datetime.datetime.now() - open_order_timestamp
                    > datetime.timedelta(seconds=strat["pause_replace"])
                ):
                    print(
                        f"OPEN Trade submitted, but not filled. Modifying order limit price: {open_trade.order.lmtPrice}"
                    )

                    # find the price of opening the trade
                    if strat["open_ref"] == "bid":
                        price_ref = ticker.domBids[0].price
                    elif strat["open_ref"] == "ask":
                        price_ref = ticker.domAsks[0].price
                    elif strat["open_ref"] == "mid":
                        price_ref = (
                            ticker.domAsks[0].price + ticker.domBids[0].price
                        ) / 2
                    else:
                        raise Exception("Not implemented")

                    limit_price = (
                        price_ref + strat["open_ticks"] * strat["tick_increment"]
                    )

                    if open_trade.order.lmtPrice == limit_price:
                        print(
                            f"Limit price of open_trade order already at {limit_price}"
                        )
                    else:
                        open_trade.order.lmtPrice = limit_price

                        print(f"Modifying open_trade order: {open_trade.order}")

                        if strat["live"]:
                            open_trade = ib.placeOrder(contract, open_trade.order)
                            push_notifications(
                                f"MODIFIED ORDER PLACED:: {open_trade.order}",
                                strat["modify_push"],
                            )
                        else:
                            print(
                                f"[NOT LIVE] MODIFIED ORDER PLACED:: {open_trade.order}"
                            )

                    open_order_timestamp = datetime.datetime.now()

            elif open_trade.orderStatus.status == "Filled" and close_trade is None:
                exec_price = open_trade.fills[0].execution.price
                print(
                    f"Filled on open_trade: {open_trade.orderStatus.status} {exec_price} {open_trade.fills[0].execution.side}"
                )

                action = strat["close_action"]
                qty = strat["close_qty"]

                # find the price to close the trade
                if strat["close_ref"] == "open_fill":
                    price_ref = exec_price
                elif strat["close_ref"] == "bid":
                    price_ref = ticker.domBids[0].price
                elif strat["close_ref"] == "ask":
                    price_ref = ticker.domAsks[0].price
                elif strat["close_ref"] == "mid":
                    price_ref = (ticker.domAsks[0].price + ticker.domBids[0].price) / 2
                else:
                    raise Exception("Not implemented")

                limit_price = price_ref + strat["close_ticks"] * strat["tick_increment"]

                if strat["close_type"] == "LIMIT":
                    close_order = LimitOrder(
                        action=action,
                        totalQuantity=qty,
                        lmtPrice=limit_price,
                        account=strat["account"],
                    )
                else:
                    raise Exception("Not implemented")

                print(f"Placing close_order {close_order}")

                if strat["live"]:
                    close_trade = ib.placeOrder(contract, close_order)
                    ib.sleep(0.1)

                    # delay push until later for speed
                    push_notifications(
                        f"OPEN ORDER FILLED:: {open_trade.order}", strat["open_push"]
                    )
                    push_notifications(
                        f"CLOSE ORDER PLACED:: {close_trade.order}", strat["close_push"]
                    )
                    alert(False)
                else:
                    print(f"[NOT LIVE] CLOSE ORDER PLACED:: {close_order}")
                    # print(f"CLOSE ORDER PLACED:: {close_trade.order}")

                refresh()

        if close_trade is not None:
            if close_trade.orderStatus.status == "Filled":
                print(f"Close trade filled @ {close_trade.orderStatus.avgFillPrice}")
                print_line()
                push_notifications(
                    f"CLOSE TRADE FILLED:: {close_trade.order}", strat["close_push"]
                )
                alert(True)

                close_order_timestamp = datetime.datetime.now()

                open_trade = None
                close_trade = None

                refresh()

            elif (
                close_trade.orderStatus.status == "Inactive"
                or close_trade.orderStatus.status == "Cancelled"
            ):
                push_notifications(
                    f"CLOSE TRADE CANCELLED:: {close_trade.order}", strat["close_push"]
                )
                close_trade = None
                refresh()


import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='My Python Script')
    parser.add_argument('--strat', type=str, help='Strategy', default='sell')
    parser.add_argument("--open_id", type=int, help="Open ID", default=0)
    parser.add_argument('--close_id', type=int, help='Close ID', default=0)
    parser.add_argument("--cancel_id", type=int, help="Cancel ID", default=0)
    parser.add_argument("--open_ticks", type=int, help="Open Ticks", default=5)
    parser.add_argument("--close_ticks", type=int, help="Close Ticks", default=-10)
    parser.add_argument("--debug", type=bool, help="Debug", default=False)
    parser.add_argument("--open_push", type=bool, help="Open Push", default=False)
    parser.add_argument("--modify_push", type=bool, help="Modify Push", default=False)
    parser.add_argument("--close_push", type=bool, help="Close Push", default=False)
    parser.add_argument("--push", type=bool, help="Push", default=True)
    parser.add_argument("--live", type=bool, help="Live", default=True)
    parser.add_argument("--margin_check", type=bool, help="Margin Check", default=True)
    parser.add_argument("--pause_replace", type=int, help="Pause Replace (sec)", default=30)
    parser.add_argument("--pause_restart", type=int, help="Pause Restart (sec)", default=30)

    args = parser.parse_args()

    if args.strat == "buy" or args.strat == "BUY_SCALP":
        STRATEGY = BUY_SCALP
    elif args.strat == "sell" or args.strat == "SELL_SCALP":
        STRATEGY = SELL_SCALP
    else:
        print(f"*** Invalid strategy {args.strat} ***")
        ib.disconnect()
        exit(0)

    if args.open_ticks != -1:
        STRATEGY["open_ticks"] = int(args.open_ticks)

    if args.close_ticks != -1:
        STRATEGY["close_ticks"] = args.close_ticks

    STRATEGY["push"] = args.push
    STRATEGY["live"] = args.live
    STRATEGY["debug"] = args.debug
    STRATEGY["open_permid"] = args.open_id
    STRATEGY["close_permid"] = args.close_id
    STRATEGY["cancel_permid"] = args.cancel_id
    STRATEGY["margin_check"] = args.margin_check
    STRATEGY["modify_push"] = args.modify_push
    STRATEGY["open_push"] = args.open_push
    STRATEGY["close_push"] = args.close_push
    STRATEGY["pause_replace"] = args.pause_replace
    STRATEGY["pause_restart"] = args.pause_restart

    try:
        pprint.pprint(f"STRATEGY CONFIG: \n {STRATEGY}")
        simple_scalp(STRATEGY)

    except KeyboardInterrupt:
        print('Interrupted')

    ib.disconnect()
    exit(0)
