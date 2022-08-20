import sqlite3
from polygon import RESTClient
import config

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

# api fetch from polygon
client = RESTClient(config.POLYGON_API_KEY)

for ticker in rows:
    print(f"processing symbol: {ticker['symbol']}")
    stock_id = stock_dict[ticker['symbol']]
    ticker_detils = client.get_ticker_details(ticker['symbol'])
    ticker_symbol = ticker['symbol']

    # active info
    active = ticker_detils.active

    # address info
    addressWrapper = ticker_detils.address
    if(addressWrapper):
        address = addressWrapper.address1
        city = addressWrapper.city
        state = addressWrapper.state
    else:
        address = None
        city = None
        state = None

    # branding info
    branding = ticker_detils.branding
    if(branding):
        logo_url = branding.logo_url
    else:
        logo_url = None

    description = ticker_detils.description
    ticker_name = ticker_detils.ticker
    list_date = ticker_detils.list_date
    market_cap = ticker_detils.market_cap
    name = ticker_detils.name
    primary_exchange = ticker_detils.primary_exchange

    cursor.execute("""
        INSERT INTO ticker_details (stock_id, active, address, city, state, logo, description, ticker, list_date, market_cap, name, primary_exchange) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (stock_id, active, address, city, state, logo_url, description, ticker_name, list_date, market_cap, name, primary_exchange))

connection.commit()