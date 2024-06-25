from tools import *

def simple_scalp(strat):

    def get_open_close_trades(open_permid, close_permid, push):
        open_trade = get_trade_by_permid(open_permid)
        close_trade = get_trade_by_permid(close_permid)

        push_notifications(
            f"{strat} / {open_permid} / {close_permid}", push
        )

        push_notifications(f"OPEN TRADE:: {open_trade}", push)
        push_notifications(f"CLOSE TRADE:: {close_trade}", push)

        return open_trade, close_trade

    local_symbol = strat["contract"]

    ticker, contract = ticker_init(local_symbol=local_symbol)

    open_trade, close_trade = get_open_close_trades(strat["open_permid"], strat["close_permid"], strat["push"])

    close_order_timestamp = None
    open_order_timestamp = None

    while ib.sleep(0.1):

        print_strategy_summary(strat, open_trade, close_trade, ticker)

        if close_order_timestamp is not None and (datetime.datetime.now() - close_order_timestamp < datetime.timedelta(seconds=strat["pause_restart"])):
            print(
                f'Waiting {strat["pause_restart"] - (datetime.datetime.now() - close_order_timestamp).seconds} seconds...'
            )
            continue

        if DEBUG:
            proceed = input("Proceed? ")

            if proceed.lower() != "y":
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

            limit_price = (
                price_ref
                + strat["open_ticks"] * strat["tick_increment"]
            )

            if strat["open_type"] == "LIMIT":
                open_order = LimitOrder(
                    action=action,
                    totalQuantity=qty,
                    lmtPrice=limit_price,
                    account=strat['account'],
                )
            else:
                raise Exception("Not implemented")

            print(f"Pre-submitting order for open_trade {open_order} ")

            open_order_state = ib.whatIfOrder(contract, open_order)

            print(f"Order state: {open_order_state}")

            if open_order_state is None:
                raise Exception(f"************ Issue placing whatIfOrder *************** ")
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

                    if LIVE:
                        open_trade = ib.placeOrder(contract, open_order)
                        ib.sleep(0.1)
                        open_order_timestamp = datetime.datetime.now()

                        trade = open_trade

                        push_notifications(f"OPEN ORDER PLACED :: #{trade.order.permId} {trade.orderStatus.status} {trade.contract.symbol} {trade.order.action} {trade.orderStatus.filled}/{trade.orderStatus.remaining} @ {trade.order.lmtPrice}", strat["open_push"])

                    else:
                        # TODO: you can mock trades here
                        print(f"[NOT LIVE] OPEN ORDER PLACED :: {open_order}")
                else:
                    print(
                        f"************ Failed Margin Check: Net Liq Value {net_liquidation_value} - {cushion} cushion < (initMarginAfter {open_order_state.initMarginAfter} | maintMarginAfter {open_order_state.maintMarginAfter}) *************** "
                    )
                    alert(False)
                    ib.sleep(5)
                    continue

        if open_trade is not None:
            if (
                open_trade.orderStatus.status == "Inactive"
                or open_trade.orderStatus.status == "Cancelled"
            ):                
                print(f"OPEN TRADE STATUS CANCELLED:: {open_trade.order}", strat["open_push"])

                for trade_entry in open_trade.log:
                    if trade_entry.status == "Cancelled" or trade_entry.message != "":
                        push_notifications(f"{trade_entry}", strat["open_push"])
                        print(f"Waiting for 200 seconds to resubmit... ")
                        ib.sleep(200)
                
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
                    print(f"OPEN Trade submitted, but not filled. Modifying order limit price: {open_trade.order.lmtPrice}")

                    # find the price of opening the trade
                    if strat["open_ref"] == "bid":
                        price_ref = ticker.domBids[0].price
                    elif strat["open_ref"] == "ask":
                        price_ref = ticker.domAsks[0].price
                    elif strat["open_ref"] == "mid":
                        price_ref = (ticker.domAsks[0].price + ticker.domBids[0].price) / 2
                    else:
                        raise Exception("Not implemented")

                    limit_price = (
                        price_ref
                        + strat["open_ticks"] * strat["tick_increment"]
                    )

                    if open_trade.order.lmtPrice == limit_price:
                        print(f"Limit price of open_trade order already at {limit_price}")
                    else:
                        open_trade.order.lmtPrice = limit_price

                        print(f"Modifying open_trade order: {open_trade.order}")

                        if LIVE:
                            open_trade = ib.placeOrder(contract, open_trade.order)
                            push_notifications(f"MODIFIED ORDER PLACED:: {open_trade.order}", strat["modify_push"])
                        else:
                            print(f"[NOT LIVE] MODIFIED ORDER PLACED:: {open_trade.order}")

                    open_order_timestamp = datetime.datetime.now()

            elif open_trade.orderStatus.status == "Filled" and close_trade is None:
                exec_price = open_trade.fills[0].execution.price
                print(f"Filled on open_trade: {open_trade.orderStatus.status} {exec_price} {open_trade.fills[0].execution.side}")

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

                limit_price = (
                    price_ref
                    + strat["close_ticks"]
                    * strat["tick_increment"]
                )

                if strat["close_type"] == "LIMIT":
                    close_order = LimitOrder(
                        action=action,
                        totalQuantity=qty,
                        lmtPrice=limit_price,
                        account=strat['account'],
                    )
                else:
                    raise Exception("Not implemented")

                print(f"Placing close_order {close_order}")

                if LIVE:
                    close_trade = ib.placeOrder(contract, close_order)
                    ib.sleep(0.1)

                    # delay push until later for speed
                    push_notifications(f"OPEN ORDER FILLED:: {open_trade.order}", strat["open_push"])
                    push_notifications(f"CLOSE ORDER PLACED:: {close_trade.order}",strat["close_push"])
                    alert(False)
                else:
                    print(f"[NOT LIVE] CLOSE ORDER PLACED:: {close_order}")
                    # print(f"CLOSE ORDER PLACED:: {close_trade.order}")

                ib.reqAllOpenOrders()
                ib.reqPositions()

        if close_trade is not None:
            if close_trade.orderStatus.status == "Filled":
                print(f"Close trade filled @ {close_trade.orderStatus.avgFillPrice}")
                print_line()
                push_notifications(f"CLOSE TRADE FILLED:: {close_trade.order}", strat["close_push"])
                alert(True)

                close_order_timestamp = datetime.datetime.now()

                open_trade = None
                close_trade = None

                ib.reqAllOpenOrders()
                ib.reqPositions()
            elif (
                close_trade.orderStatus.status == "Inactive"
                or close_trade.orderStatus.status == "Cancelled"
            ):                
                push_notifications(f"CLOSE TRADE CANCELLED:: {close_trade.order}", strat["close_push"])
                close_trade = None
        
        # ib.reqAllOpenOrders()


if __name__ == "__main__":
    try:
        simple_scalp(STRATEGY)

    except KeyboardInterrupt:
        ib.disconnect()

        print("Exiting...")
        exit(0)
