# Crypto Trading Bot for Binance

The provided code implements a basic trading strategy using the Backtrader library, focused on buying and selling assets on the Binance exchange. Let's break down the code and discuss its functionality.

The code begins by importing necessary modules and libraries: **datetime**, **backtrader**, and the **Binance** extension for Backtrader. Additionally, set your API keys and other settings related to the Binance exchange.

```shell
import datetime as dt
import backtrader as bt
from backtrader_binance import BinanceStore

BINANCE_API_KEY = "YOUR_BINANCE_API_KEY"
BINANCE_API_SECRET = "YOUR_BINANCE_API_SECRET"

```

Following the imports, the code defines a trading strategy class named JustBuySellStrategy, which inherits from **bt.Strategy**. This strategy is designed for live trading and performs simple buy and sell actions.

```commandline
class JustBuySellStrategy(bt.Strategy):
    """
    Live strategy demonstration - just buy and sell
    """
    params = (
        ('coin_target', ''),
    )

```

The **__init__** method initializes the strategy and sets up necessary data structures. It creates an empty dictionary orders to store orders for each ticker.

```commandline
def __init__(self):
    """Initialization, adding indicators for each ticker"""
    self.orders = {}  # All orders as a dict, for this particularly trading strategy one ticker is one order
    for d in self.datas:  # Running through all the tickers
        self.orders[d._name] = None  # There is no order for ticker yet

```

The next method is where the strategy's main logic resides. It iterates over each data feed (ticker) and checks its status (live or historical). If the data is live, it retrieves relevant information such as open, high, low, close prices, and volume. It also prints out this information along with the data's status.

```commandline
def next(self):
    """Arrival of a new ticker candle"""
    for data in self.datas:  # Running through all the requested bars of all tickers
        ticker = data._name
        status = data._state  # 0 - Live data, 1 - History data, 2 - None
        _interval = self.broker._store.get_interval(data._timeframe, data._compression)

```

If the data is live, the strategy checks for existing positions and places buy orders accordingly. It also handles canceling existing orders if necessary.

```commandline
if status == 0:  # Live trade
    coin_target = self.p.coin_target
    ...
    if not self.getposition(data):  # If there is no position
        ...
        self.orders[data._name] = self.buy(data=data, exectype=bt.Order.Market, size=size)
        print(f"\t - The Market order has been submitted {self.orders[data._name].binance_order['orderId']} to buy {data._name}")

```

The notify_order method is called whenever the status of an order changes. It logs relevant information about the order, such as its status, type (buy or sell), price, and size.

```commandline
def notify_order(self, order):
    """Changing the status of the order"""
    order_data_name = order.data._name  # Name of ticker from order
    self.log(f'Order number {order.ref} {order.info["order_number"]} {order.getstatusname()} {"Buy" if order.isbuy() else "Sell"} {order_data_name} {order.size} @ {order.price}')

```

Similarly, the notify_trade method is called when a trade (position) is closed. It logs information about the profit or loss from the closed position.

```commandline
def notify_trade(self, trade):
    """Changing the position status"""
    if trade.isclosed:  # If the position is closed
        self.log(f'Profit on a closed position {trade.getdataname()} Total={trade.pnl:.2f}, No commission={trade.pnlcomm:.2f}')

```

Lastly, the log method is a utility function to print messages along with timestamps to the console.

```commandline
def log(self, txt, dt=None):
    """Print string with date to the console"""
    dt = bt.num2date(self.datas[0].datetime[0]) if not dt else dt  # date or date of the current bar
    print(f'{dt.strftime("%d.%m.%Y %H:%M")}, {txt}')  # Print the date and time with the specified text to the console

```

The main part of the script initializes the Backtrader framework (cerebro), sets up the Binance data store and broker, configures data retrieval for a specific symbol (ETH/USDT), adds the data and strategy to cerebro, and finally runs the strategy.

```commandline
if __name__ == '__main__':
    cerebro = bt.Cerebro(quicknotify=True)

    coin_target = 'USDT'  # the base ticker in which calculations will be performed
    symbol = 'ETH' + coin_target  # the ticker by which we will receive data in the format <CodeTickerBaseTicker>

    store = BinanceStore(
        api_key=Config.BINANCE_API_KEY,
        api_secret=Config.BINANCE_API_SECRET,
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

```

In summary, the code demonstrates a simple live trading strategy using Backtrader and Binance API for data retrieval and trading execution. It buys assets based on certain conditions and logs relevant information about orders, trades, and positions.

## License
[MIT](https://choosealicense.com/licenses/mit)

## Important
Error correction, revision and development of the library is carried out by the author and the community!

**Push your commits!**

## Terms of Use
The backtrader_binance library, which allows you to integrate Backtrader and Binance API, is the **Program** created solely for the convenience of work.
When using the **Program**, the User is obliged to comply with the provisions of the current legislation of his country.
Using the **Program** are offered on an "AS IS" basis. No guarantees, either oral or written, are attached and are not provided.
The author and the community does not guarantee that all errors of the **Program** have been eliminated, respectively, the author and the community do not bear any responsibility for
the consequences of using the **Program**, including, but not limited to, any damage to equipment, computers, mobile devices,
User software caused by or related to the use of the **Program**, as well as for any financial losses
incurred by the User as a result of using the **Program**.
No one is responsible for data loss, losses, damages, including accidental or indirect, lost profits, loss of revenue or any other losses
related to the use of the **Program**.

The **Program** is distributed under the terms of the [MIT](https://choosealicense.com/licenses/mit ) license.
