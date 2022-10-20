# easy function  get accounts from tinkoff API

import tinvest
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.environ.get('token_tf')


def accounts_info():
    client = tinvest.SyncClient(TOKEN)
    return client.get_accounts().payload.accounts  # получаю данные по аккаунта


if __name__ == '__main__':
    accounts_info = accounts_info()
    print(f"{accounts_info[0].broker_account_type.split('.')[0]} - {accounts_info[0].broker_account_id}")
    print(f"{accounts_info[1].broker_account_type.split('.')[0]} - {accounts_info[1].broker_account_id}")
