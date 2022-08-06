from lib2to3.pytree import type_repr
from polygon import RESTClient
import config

client = RESTClient(config.POLYGON_API_KEY)


print(client.get_ticker_details(ticker='AAPL'))