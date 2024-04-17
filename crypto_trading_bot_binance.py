# pip install backtrader_binance

import datetime as dt
import backtrader as bt
from backtrader_binance import BinanceStore

BINANCE_API_KEY = "YOUR_BINANCE_API_KEY"
BINANCE_API_SECRET = "YOUR_BINANCE_API_SECRET"


# Trading System
class JustBuySellStrategy(bt.Strategy):
    """
    Live strategy demonstration - just buy and sell
    """
    params = (  # Parameters of the trading system
        ('coin_target', ''),
    )

    def __init__(self):
        """Initialization, adding indicators for each ticker"""
        self.orders = {}  # All orders as a dict, for this particularly trading strategy one ticker is one order
        for d in self.datas:  # Running through all the tickers
            self.orders[d._name] = None  # There is no order for ticker yet

    def next(self):
        """Arrival of a new ticker candle"""
        for data in self.datas:  # Running through all the requested bars of all tickers
            ticker = data._name
            status = data._state  # 0 - Live data, 1 - History data, 2 - None
            _interval = self.broker._store.get_interval(data._timeframe, data._compression)

            if status in [0, 1]:
                if status: _state = "False - History data"
                else: _state = "True - Live data"

                print('{} / {} [{}] - Open: {}, High: {}, Low: {}, Close: {}, Volume: {} - Live: {}'.format(
                    bt.num2date(data.datetime[0]),
                    data._name,
                    _interval,  # ticker timeframe
                    data.open[0],
                    data.high[0],
                    data.low[0],
                    data.close[0],
                    data.volume[0],
                    _state,
                ))

                if status == 0:  # Live trade
                    coin_target = self.p.coin_target
                    print(f"\t - Free balance: {self.broker.getcash()} {coin_target}")
                    # Very slow function! Because we are going through API to get those values...
                    symbol_balance, short_symbol_name = self.broker._store.get_symbol_balance(ticker)
                    print(f"\t - {ticker} current balance = {symbol_balance} {short_symbol_name}")

                    order = self.orders[data._name]  # The order of ticker
                    if order and order.status == bt.Order.Submitted:  # If the order is not on the exchange (sent to the broker)
                        return  # then we are waiting for the order to be placed on the exchange, we leave, we do not continue further

                    if not self.getposition(data):  # If there is no position
                        print("there is no position")

                        # if we have order but don't get position -> then cancel it
                        if order and order.status == bt.Order.Accepted:  # If the order is on the exchange (accepted by the broker)
                            print(f"\t - Cancel the order {order.binance_order['orderId']} to buy {data._name}")
                            self.cancel(order)  # then cancel it

                        size = float(self.broker._store._min_order[ticker])   # min value to buy for BTC and ETH
                        min_in_USDT = float(self.broker._store._min_order_in_target[ticker])   # min value to buy for BTC and ETH
                        _close = data.close[0]
                        # correct size to be minimum applicable volume
                        if size * _close < min_in_USDT: size = min_in_USDT / _close
                        size = float(self.broker._store.format_quantity(ticker, size))

                        # # Set Limit order
                        # # Let's buy min value of ticker - min_order by price lower on 5% from current
                        # price = float(self.broker._store.format_price(ticker, data.low[0] * 0.95))  # 5% lower than the min price
                        # # correct size to be minimum applicable volume
                        # if size * price < min_in_USDT: size = min_in_USDT / price
                        # size = float(self.broker._store.format_quantity(ticker, size))
                        #
                        # print(f" - buy {ticker} size = {size} (min_order) at price = {price}")
                        # self.orders[data._name] = self.buy(data=data, exectype=bt.Order.Limit, price=price, size=size)
                        # print(f"\t - The Limit order has been submitted {self.orders[data._name].binance_order['orderId']} to buy {data._name}")

                        # Set Market order
                        # Let's buy just a little amount by market price
                        print(f" - buy {ticker} size = {size} (min_order) at Market price")
                        self.orders[data._name] = self.buy(data=data, exectype=bt.Order.Market, size=size)
                        print(f"\t - The Market order has been submitted {self.orders[data._name].binance_order['orderId']} to buy {data._name}")

    def notify_order(self, order):
        """Changing the status of the order"""
        order_data_name = order.data._name  # Name of ticker from order
        self.log(f'Order number {order.ref} {order.info["order_number"]} {order.getstatusname()} {"Buy" if order.isbuy() else "Sell"} {order_data_name} {order.size} @ {order.price}')
        if order.status == bt.Order.Completed:  # If the order is fully executed
            if order.isbuy():  # The order to buy
                self.log(f'Buy {order_data_name} Price: {order.executed.price:.2f}, Value {order.executed.value:.2f} {self.p.coin_target}, Commission {order.executed.comm:.10f} {self.p.coin_target}')
            else:  # The order to sell
                self.log(f'Sell {order_data_name} Price: {order.executed.price:.2f}, Value {order.executed.value:.2f} {self.p.coin_target}, Commission {order.executed.comm:.10f} {self.p.coin_target}')
            self.orders[order_data_name] = None  # Reset the order to enter the position

    def notify_trade(self, trade):
        """Changing the position status"""
        if trade.isclosed:  # If the position is closed
            self.log(f'Profit on a closed position {trade.getdataname()} Total={trade.pnl:.2f}, No commission={trade.pnlcomm:.2f}')

    def log(self, txt, dt=None):
        """Print string with date to the console"""
        dt = bt.num2date(self.datas[0].datetime[0]) if not dt else dt  # date or date of the current bar
        print(f'{dt.strftime("%d.%m.%Y %H:%M")}, {txt}')  # Print the date and time with the specified text to the console


if __name__ == '__main__':
    cerebro = bt.Cerebro(quicknotify=True)

    coin_target = 'USDT'  # the base ticker in which calculations will be performed
    symbol = 'ETH' + coin_target  # the ticker by which we will receive data in the format <CodeTickerBaseTicker>

    store = BinanceStore(
        api_key=BINANCE_API_KEY,
        api_secret=BINANCE_API_SECRET,
        coin_target=coin_target,
        testnet=False)  # Binance Storage

    # live connection to Binance - for Offline comment these two lines
    broker = store.getbroker()
    cerebro.setbroker(broker)

    # Historical 1-minute bars for the last hour + new live bars / timeframe M1
    from_date = dt.datetime.utcnow() - dt.timedelta(minutes=5)
    data = store.getdata(timeframe=bt.TimeFrame.Minutes, compression=1, dataname=symbol, start_date=from_date, LiveBars=True)

    cerebro.adddata(data)  # Adding data

    cerebro.addstrategy(JustBuySellStrategy, coin_target=coin_target)  # Adding a trading system

    cerebro.run()  # Launching a trading system
    cerebro.plot()  # Draw a chart
