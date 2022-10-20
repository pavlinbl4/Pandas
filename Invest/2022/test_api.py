import tinvest
import datetime
import os
from dotenv import load_dotenv
import ast

load_dotenv()
TOKEN = os.environ.get('token_tf')

accounts_id = ast.literal_eval(os.environ.get('account_id'))

client = tinvest.SyncClient(TOKEN)

print(type(accounts_id))
response = client.get_portfolio(broker_account_id=accounts_id['iis']).payload  # получаю портфолио по аккаунту

# Получение инструмента по FIGI
response = client.get_market_search_by_figi('BBG000BL8476').payload
print(response)

# Получение инструмента по ticker
response = client.get_market_search_by_ticker("FFIN").payload.instruments
print(response)

response = client. \
    get_operations(from_='2022-01-01T09:38:33+03:00',
                   to=datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()) \
    .payload.operations
