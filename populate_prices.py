from re import T
import sqlite3
import config
import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import TimeFrame
from datetime import datetime
from datetime import date
from datetime import timedelta

import tulipy
import numpy

connection = sqlite3.connect(config.DB_FILE)
connection.row_factory = sqlite3.Row

cursor = connection.cursor()

cursor.execute("""
    SELECT id, symbol, name from stock
""")

rows = cursor.fetchall()
symbols = []

stock_dict = {}
for row in rows:
    symbol = row['symbol']
    symbols.append(symbol)
    stock_dict[symbol] = row['id']

api = tradeapi.REST(config.API_KEY, config.SECRET_KEY,
                    base_url=config.BASE_URL)

cursor.execute("""
    SELECT MAX(date) FROM stock_price
""")
lastClosePrice = cursor.fetchone()
chunk_size = 200

yesterDayDate = date.today() - timedelta(days=1)
PastDate = yesterDayDate - timedelta(days=100)
dayBeforeYesterDayDate = date.today() - timedelta(days=2)
day_name= ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday','Sunday']
yesterDay = datetime.strptime(str(yesterDayDate), '%Y-%m-%d').weekday()
dayBeforeYesterDay = datetime.strptime(str(dayBeforeYesterDayDate), '%Y-%m-%d').weekday()

# symbols = ['DOGE/USD', 'DOGE/USDT', 'MATIC/USD', 'SOL/BTC', 'MATIC/BTC', 'MKR/USD', 'NEAR/USD', 'NEAR/USDT', 'SOL/USDT']
# symbols = ['DOGE/USD', 'RYAAY', 'BTWNU', 'RYAM', 'RYAN']
invalid_symbols = []
for i in range(0, len(symbols), chunk_size):
    symbol_chunk = []
    for symbol in symbols[i: i+chunk_size]:
        if '/' in symbol:
            invalid_symbols.append(symbol)
        else:
            symbol_chunk.append(symbol)
    if len(symbol_chunk) > 0:
        barsets = api.get_bars_iter(
            symbol_chunk, TimeFrame.Day, yesterDayDate, yesterDayDate, adjustment='raw')
    
    recent_closes = []
    sma_20, sma_50, rsi_14 = None, None, None
    for symbol in barsets:        
        print(f"processign symbol {symbol.S}")
        recent_closes.append(symbol.c)

        if len(recent_closes) >= 50 and yesterDayDate == symbol.t.date():
            sma_20 = tulipy.sma(numpy.array(recent_closes), period=20)[-1]
            sma_50 = tulipy.sma(numpy.array(recent_closes), period=50)[-1]
            rsi_14 = tulipy.rsi(numpy.array(recent_closes), period=14)[-1]
        elif len(recent_closes) >= 50 and (day_name[yesterDay] == 'Sunday' or day_name[dayBeforeYesterDay] == 'Saturday'):
            sma_20 = tulipy.sma(numpy.array(recent_closes), period=20)[-1]
            sma_50 = tulipy.sma(numpy.array(recent_closes), period=50)[-1]
            rsi_14 = tulipy.rsi(numpy.array(recent_closes), period=14)[-1]
        stock_id = stock_dict[symbol.S]

        cursor.execute("""
            INSERT INTO stock_price (stock_id, date, open, high, low, close, volume, sma_20, sma_50, rsi_14)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (stock_id, symbol.t.date(), symbol.o, symbol.h, symbol.l, symbol.c, symbol.v, sma_20, sma_50, rsi_14))
print("Not able to get the bar data for these symbols", invalid_symbols)

connection.commit()
