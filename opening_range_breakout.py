import sqlite3, config
import alpaca_trade_api as tradeapi
import datetime as date
from alpaca_trade_api.rest import REST, TimeFrame, TimeFrameUnit

connection = sqlite3.connect(config.DB_FILE)
connection.row_factory =sqlite3.Row

cursor = connection.cursor()

cursor.execute("""
    SELECT id from strategy WHERE name='opening_range_breakout'
""")

strategy_id = cursor.fetchone()['id']

cursor.execute("""
    SELECT symbol, name FROM stock JOIN stock_strategy ON
    stock_strategy.stock_id = stock.id
    WHERE stock_strategy.strategy_id = ?
""", (strategy_id ,))

stocks = cursor.fetchall()

# print(stocks)

symbols = [stock['symbol'] for stock in stocks]

api = tradeapi.REST(config.API_KEY, config.SECRET_KEY, base_url=config.BASE_URL)


for symbol in symbols:
    minute_bars = api.get_bars([symbol], TimeFrame(1, TimeFrameUnit.Minute), "2022-07-21", "2022-07-21", adjustment='raw').df
    print(symbol, minute_bars)