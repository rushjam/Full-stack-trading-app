import sqlite3
import config
import yfinance as yf

from urllib import response
from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from fastapi.templating import Jinja2Templates
from datetime import date
from datetime import datetime
from datetime import timedelta
from numerize import numerize


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/")
def index(request: Request):
    stock_filter = request.query_params.get('filter', False)
    yesterDayDate = date.today() - timedelta(days=1)
    connection = sqlite3.connect(config.DB_FILE)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    if stock_filter == 'new_closing_highs':
        cursor.execute("""
            SELECT * FROM (
                SELECT symbol, name, stock_id, max(close), date
                FROM stock_price JOIN stock ON stock.id = stock_price.stock_id
                GROUP BY stock_id
                ORDER By symbol
                )
                WHERE date = (SELECT MAX(date) FROM stock_price)
        """)
    elif stock_filter == 'rsi_overbought':
        cursor.execute("""
                SELECT symbol, name, stock_id, date
                FROM stock_price JOIN stock ON stock.id = stock_price.stock_id
                WHERE rsi_14 > 70
                AND date = (SELECT MAX(date) FROM stock_price)
                ORDER BY symbol
        """)
    elif stock_filter == 'rsi_oversold':
        cursor.execute("""
                SELECT symbol, name, stock_id, date
                FROM stock_price JOIN stock ON stock.id = stock_price.stock_id
                WHERE rsi_14 < 30
                AND date = (SELECT MAX(date) FROM stock_price)
                ORDER BY symbol
        """)
    elif stock_filter == 'above_sma_20':
        cursor.execute("""
                SELECT symbol, name, stock_id, date
                FROM stock_price JOIN stock ON stock.id = stock_price.stock_id
                WHERE close > sma_20
                AND date = (SELECT MAX(date) FROM stock_price)
                ORDER BY symbol
        """)
    elif stock_filter == 'below_sma_20':
        cursor.execute("""
                SELECT symbol, name, stock_id, date
                FROM stock_price JOIN stock ON stock.id = stock_price.stock_id
                WHERE close < sma_20
                AND date = (SELECT MAX(date) FROM stock_price)
                ORDER BY symbol
        """)
    elif stock_filter == 'above_sma_50':
        cursor.execute("""
                SELECT symbol, name, stock_id, date
                FROM stock_price JOIN stock ON stock.id = stock_price.stock_id
                WHERE close > sma_50
                AND date = (SELECT MAX(date) FROM stock_price)
                ORDER BY symbol
        """)
    elif stock_filter == 'below_sma_50':
        cursor.execute("""
                SELECT symbol, name, stock_id, date
                FROM stock_price JOIN stock ON stock.id = stock_price.stock_id
                WHERE close < sma_50
                AND date = (SELECT MAX(date) FROM stock_price)
                ORDER BY symbol
        """)
    else:
        cursor.execute("""
            SELECT id, symbol, name FROM stock ORDER BY symbol  LIMIT 100
        """)
    rows = cursor.fetchall()

    cursor.execute("""
        SELECT symbol, rsi_14, sma_20, sma_50, close FROM stock JOIN  stock_price on stock_price.stock_id = stock.id WHERE date = (SELECT MAX(date) FROM stock_price)
    """)

    indicator_rows = cursor.fetchall()
    indicator_values = {}
    for row in indicator_rows:
        indicator_values[row['symbol']] = row
    return templates.TemplateResponse("index.html", {"request": request, "stocks": rows, "indicator_values": indicator_values})


@app.get("/stock/")
def stock_detail(request: Request):
    symbol = request.query_params.get('abb', False)
    connection = sqlite3.connect(config.DB_FILE)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM strategy
    """)

    strategies = cursor.fetchall()

    cursor.execute("""
        SELECT id, symbol, name FROM stock WHERE symbol = ?
    """, (symbol,))

    row = cursor.fetchone()

    cursor.execute("""
        SELECT * FROM stock_price WHERE stock_id = ?
    """, (row['id'], ))
    bars = cursor.fetchall()
    
    # yfinanace data
    yfinance = yf.Ticker(row['symbol'])
    # yfinance.history(period="max", proxy="https://10.10.1.10:1080")
    stock_details = yfinance.info   
    stock_news = yfinance.news

    def numberConversion(number):
        if number:
            return numerize.numerize(number)
        else:
            return None
    def dataChecker(checkerObj, key):
        if key in checkerObj:
            return checkerObj[key]
        else:
            return None    
    def roundOf(number, upTo):
        if number:
            return round(number * 100, upTo)
    
    # marketdata
    marketCap = dataChecker(stock_details, 'marketCap')
    volume = dataChecker(stock_details, 'volume')
    volume24Hr = dataChecker(stock_details, 'volume24Hr')
    _52WeekChange = dataChecker(stock_details, '52WeekChange')
    previousClose = dataChecker(stock_details, 'previousClose')
    dayHigh = dataChecker(stock_details, 'dayHigh')
    dayLow = dataChecker(stock_details, 'dayLow')
    regularMarketOpen = dataChecker(stock_details, 'regularMarketOpen')
    exchange = dataChecker(stock_details, 'exchange')
    logo_url = dataChecker(stock_details, 'logo_url')
    longBusinessSummary = dataChecker(stock_details, 'longBusinessSummary')
    website = dataChecker(stock_details, 'website')
    industry = dataChecker(stock_details, 'industry')
    startDate = dataChecker(stock_details, 'industry')
    sector = dataChecker(stock_details, 'sector')
        
    marketData = {
        "marketCap": numberConversion(marketCap),
        "volume": numberConversion(volume),
        "52WeekChange": roundOf(_52WeekChange, 2),
        "previousClose": previousClose,
        "dayHigh": dayHigh,
        "dayLow": dayLow,
        "regularMarketOpen": regularMarketOpen,
        "logo_url": logo_url,
        "longBusinessSummary": longBusinessSummary,
        "website": website,
        "industry": industry,
        "startDate": startDate,
        "sector": sector,
        "exchange": exchange
    }

    newsData = []
    for index, news in enumerate(stock_news):
        newsObj = {}
        newsObj['id'] = index
        if 'title' in news:
            newsObj['title'] = news['title']
        if 'link' in news:
            newsObj['link'] = news['link']
        if 'thumbnail' in news:
            newsObj['thumbnail'] = news['thumbnail']
        if 'providerPublishTime' in news:
            
            miliSec = datetime.fromtimestamp(news['providerPublishTime'])
            reableDate = miliSec.strftime('%m/%d/%Y')
            newsObj['date'] = reableDate
        newsData.append(newsObj) 
    
    return templates.TemplateResponse("stock_detail.html", {"request": request, "stock": row, "bars": bars, "strategies": strategies, "marketData": marketData, "stock_details": stock_details, "newsData": newsData})


@app.post("/apply_strategy")
def apply_strategy(strategy_id: int = Form(...), stock_id: int = Form(...)):
    connection = sqlite3.connect(config.DB_FILE)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO stock_strategy (stock_id, strategy_id) VALUES (?, ?)
    """, (stock_id, strategy_id))

    connection.commit()

    return RedirectResponse(url=f"/strategy/{strategy_id}", status_code=303)


@app.get('/strategies')
def strategies(request: Request):
    connection = sqlite3.connect(config.DB_FILE)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("""
        SELECT * FROM strategy
    """)
    strategies = cursor.fetchall()
    return templates.TemplateResponse("strategies.html", {"request": request, "strategies": strategies})


@app.get("/strategy/{strategy_id}")
def strategy(request: Request, strategy_id):
    connection = sqlite3.connect(config.DB_FILE)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, name
        FROM strategy
        WHERE id = ?
    """, (strategy_id, ))

    strategy = cursor.fetchone()

    cursor.execute("""
        SELECT symbol, name 
        FROM stock JOIN stock_strategy on stock_strategy.stock_id = stock.id
        WHERE strategy_id = ?
    """, (strategy_id, )
    )

    stocks = cursor.fetchall()

    return templates.TemplateResponse("strategy.html", {"request": request, "stocks": stocks, "strategy": strategy})
