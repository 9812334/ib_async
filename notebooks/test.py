########################################
## SELL TO OPEN SCALP 0.1
########################################

strategy_details = {
    "strategy": "SELL TO OPEN SCALP 0.1",
    "contract": "NQM2024",
    "tick_increment": 0.25,
    "open_qty": 1,
    "open_type": "LIMIT",
    "open_action": "SELL",
    "open_ref": "bid",
    "open_ticks": 10,
    "close_qty": 1,
    "close_type": "LIMIT",
    "close_ref": "open_price_fill",
    "close_ticks": -10
    }

while True:
    clear_output(wait=True)  # Clear the output before printing new output

    # first order of the strategy
    if open_trade is None and close_trade is None:
        action = strategy_details['open_action']
        totalQuantity = strategy_details['open_qty']
        
        if strategy_details('open_ref') == 'bid':
            price_ref = ticker.domBids[0].price
        elif strategy_details('open_ref') == 'ask':
            price_ref = ticker.domAsks[0].price
        elif strategy_details('open_ref') == 'mid':
            price_ref = (ticker.domAsks[0].price + ticker.domBids[0].price)/2
        elif strategy_details('open_ref') == 'last':
            raise Exception('Not implemented')

        lmtPrice = price_ref + strategy_details['open_ticks'] * strategy_details['tick_increment']
        print(f"Placing open trade: {action}, {strategy_details['open_type']}, totalQuantity {totalQuantity}, lmtPrice {lmtPrice}")
        print()

        if strategy_details['open_type'] == "LIMIT":
            open_order = LimitOrder(
                action=action,
                totalQuantity=totalQuantity,
                lmtPrice=lmtPrice,
                account="U10394496",
            )
        else:
            raise Exception('Not implemented')
            
        open_trade = ib.placeOrder(contract, open_order)
        open_order_ts = datetime.datetime.now()
        ib.sleep(1)
        play_beep()


    print("OPEN ORDER::")
    print_order(open_trade)
    print()

    if open_trade is not None:
        if open_trade.orderStatus.status == "Submitted" and close_trade is None:
            print(
                f"Waiting to get filled L1 {open_trade.order.permId} {open_trade.orderStatus.status}"
            )

            if datetime.datetime.now() - open_order_ts > datetime.timedelta(minutes=5):
                print("Cancelling order due to timeout")
                ib.cancelOrder(open_trade.order)
                ib.sleep(1)
                print(open_trade.log)
            print()
            
        if open_trade.orderStatus.status == "Filled" and close_trade is None:
            action = strategy_details['close_action']
            totalQuantity = strategy_details['close_qty']
            
            if strategy_details('close_ref') == 'open_price_fill':
                price_ref = open_trade.orderStatus.avgFillPrice
            if strategy_details('close_ref') == 'bid':
                price_ref = ticker.domBids[0].price
            elif strategy_details('close_ref') == 'ask':
                price_ref = ticker.domAsks[0].price
            elif strategy_details('close_ref') == 'mid':
                price_ref = (ticker.domAsks[0].price + ticker.domBids[0].price)/2
            elif strategy_details('close_ref') == 'last':
                raise Exception('Not implemented')
            
            lmtPrice = price_ref + strategy_details['close_ticks'] * strategy_details['tick_increment']
            print(f"Placing close trade: {action}, {strategy_details['close_type']}, totalQuantity {totalQuantity}, lmtPrice {lmtPrice}")
            
            if strategy_details['close_type'] == "LIMIT":
                close_order = LimitOrder(
                    action=action,
                    totalQuantity=totalQuantity,
                    lmtPrice=lmtPrice,
                    account="U10394496",
                )
            else:
                raise Exception('Not implemented')
            
            close_trade = ib.placeOrder(contract, close_order)
            ib.sleep(1)
            play_beep()
        elif (
            open_trade.orderStatus.status == "Inactive"
            or open_trade.orderStatus.status == "Cancelled"
        ) and close_trade is None:
            print("***** order is inactive *****")
            print(open_trade.log)
            print("*****************************")
            open_trade = None

    print(f"CLOSE ORDER::")
    print_order(close_trade)

    if close_trade is not None:
        if close_trade.orderStatus.status == "Filled":
            play_beep()
            print("Close trade filled @ {}".format(close_trade.orderStatus.avgFillPrice))
            open_trade = None
            close_trade = None
    print()
    print()
    print("ALL OPEN ORDERS:")
    print_all_openorders(ib=ib)
    print()

    # get current position of contract NQM2024
    print("Current position:")
    print(
        f"{future.contract.symbol}:  {future.position} @ {future.avgCost/float(contract.multiplier)}"
    )

    print_account_summary(ib=ib)
    print()
    for i in range(5):
        print(".", end="")
        time.sleep(1)