# test script to get portfolio IIS


import tinvest
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.environ.get('token_tf')
account_iis = os.environ.get('account_iis')

client = tinvest.SyncClient(TOKEN)

response = client.get_portfolio(broker_account_id=account_iis).payload  # ИИС

data = response.positions

for i in data:
    print(i)
