import sqlite3
import config

connection = sqlite3.connect(config.DB_FILE)

cursor = connection.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock (
        id INTEGER PRIMARY KEY,
        symbol TEXT NOT NULL UNIQUE,
        name TEXT NOT NULL,
        exchange TEXT NOT NULL
    )
    """
               )

cursor.execute("""
    CREATE TABLE IF NOT EXISTS ticker_details (
        id INTEGER PRIMARY KEY,
        stock_id INTEGER,
        active BOOLEAN,
        address TEXT,
        city TEXT,
        state TEXT,
        logo TEXT,
        description TEXT,
        ticker TEXT,
        list_date DATE,
        market_cap INTEGER,
        name TEXT,
        primary_exchange TEXT,
        FOREIGN KEY (stock_id) REFERENCES stock (id)
    )
    """
                )

cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock_price (
    id INTEGER PRIMARY KEY, 
    stock_id INTEGER,
    date NOT NULL,
    open NOT NULL, 
    high NOT NULL,
    low NOT NULL, 
    close NOT NULL,
    volume NOT NULL,
    sma_20,
    sma_50,
    rsi_14,
    FOREIGN KEY (stock_id) REFERENCES stock (id)
    )
    """
               )

cursor.execute("""
        CREATE TABLE IF NOT EXISTS strategy (
            id INTEGER PRIMARY KEY,
            name NOT NULL,
            desc TEXT NOT NULL
        )
        """
               )

cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_strategy (
            stock_id INTEGER NOT NULL,
            strategy_id INTEGER NOT NULL,
            FOREIGN KEY (stock_id) REFERENCES stock(id),
            FOREIGN KEY (strategy_id) REFERENCES strategy(id)
        )
    """)

strategies = [['Opening Range Breakout', 'Due to high significance and non-random price movement, the open gives plenty of insights to build a successful trading strategy. It is often associated with high volume and volatility with multiple trading opportunities. Traders use the opening range to set entry and predict the price action of the day. The theory gained steam during the 1990s when traders started to use the trading signals from the first hour or the opening range to set their strategy. Later though, with the availability of advanced software and data, traders also used 15-minutes and 30-minutes timeframes, but the name stuck on.'],
              ['Opening Range Breakdown', 'Due to high significance and non-random price movement, the open gives plenty of insights to build a successful trading strategy. It is often associated with high volume and volatility with multiple trading opportunities. Traders use the opening range to set entry and predict the price action of the day. The theory gained steam during the 1990s when traders started to use the trading signals from the first hour or the opening range to set their strategy. Later though, with the availability of advanced software and data, traders also used 15-minutes and 30-minutes timeframes, but the name stuck on.'], 
              ['Bollinger Bands', 'Due to high significance and non-random price movement, the open gives plenty of insights to build a successful trading strategy. It is often associated with high volume and volatility with multiple trading opportunities. Traders use the opening range to set entry and predict the price action of the day. The theory gained steam during the 1990s when traders started to use the trading signals from the first hour or the opening range to set their strategy. Later though, with the availability of advanced software and data, traders also used 15-minutes and 30-minutes timeframes, but the name stuck on.']]

for strategy in strategies:
    cursor.execute("""
        INSERT INTO strategy (name, desc) VALUES (?, ?)
    """, (strategy[0], strategy[1],))

connection.commit()
