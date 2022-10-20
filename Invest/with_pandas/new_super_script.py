"""
скипт обращается к тинькофф API и создает файлы для дальнейшего анализа
с момента открытия по сегодняшний день. те это расширенный скрпипт  operations
"""

import tinvest
import pandas as pd
import datetime
import subprocess
import csv
from dotenv import load_dotenv
import ast
import os

load_dotenv()
TOKEN = os.environ.get('token_tf')
account_id = ast.literal_eval(os.environ.get('account_id'))

today_data = datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()
filename_data = datetime.date.today()


client = tinvest.SyncClient(TOKEN)

accounts_info = client.get_accounts().payload.accounts  # получаю данные по аккаунта
df = pd.DataFrame([s.dict() for s in accounts_info])  # датафрэйм с данными аккаунта


csv_file_path = '/Volumes/big4photo/Documents/Инвестиции'  # для модуля по денежным  остаткам
file_name = "Валюта_на_счете"  # для модуля по денежным  остаткам
API_folder = '/Volumes/big4photo/Documents/Инвестиции/API_data'


# функции для модуля по денежным остаткам create_csv(work_file)

def get_portfolio(client, account):
    return pd.DataFrame([s.dict() for s in client.get_portfolio(broker_account_id=account).payload.positions])


def create_csv(
        work_file):  # создаю файл отчета - одноразовая операция write_csv(data, filename_data, work_file), currency_report(client, account)
    with open(work_file, 'a') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(('Дата', 'EUR', 'RUB', 'USD'))


def write_csv(data, filename_data, work_file):  # записваю данные в файл отчета  для каждого счета
    with open(work_file, 'a') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow((filename_data, data[0].balance, data[1].balance, data[2].balance))


def currency_report(client, account):  # получаю список с данными по валютам на счете
    return client.get_portfolio_currencies(broker_account_id=account).payload.currencies


def operations_response(today_data, account_id):  # получаю отчет по операциям для заданного аккаунта
    return client \
        .get_operations(from_='2020-09-01T18:38:33+03:00', to=today_data, broker_account_id=account_id) \
        .payload \
        .operations


def create_all_bonds_file(client):
    response = client.get_market_bonds().payload.instruments  # просмотр облигаций

    df = pd.DataFrame([s.dict() for s in response])
    df = df[['name', 'ticker', 'figi', 'currency']] \
        .sort_values('name')

    df.to_excel(f'{API_folder}/all_brokers_bonds.xlsx', index=False)


def create_df_from_csv(k):
    return \
        pd.read_csv(
            f'/Volumes/big4photo/Documents/Инвестиции/API_data/{filename_data}/operations_{k}_{filename_data}.csv') \
            [['operation_type', 'payment']] \
            .groupby(['operation_type'], as_index=False) \
            .aggregate({'payment': sum})


create_all_bonds_file(client)  # создаю файл по всем облигациям у тинькова

os.makedirs(f"/Volumes/big4photo/Documents/Инвестиции/API_data/{filename_data}",
            exist_ok=True)  # создаю папку для сохранения страниц, если папка есть, то она остается

bonds = pd.read_excel('/Volumes/big4photo/Documents/Инвестиции/API_data/all_brokers_bonds.xlsx')
bonds_name = bonds[['figi', 'name', 'ticker']]  # создаю датафрэйм с именами облигаций


for account_name in account_id:
    pd.DataFrame([s.dict() for s in operations_response(today_data, account_id[account_name])]) \
        .to_csv(
        f'/Volumes/big4photo/Documents/Инвестиции/API_data/{filename_data}/operations_{account_name}_{filename_data}.csv') # сохраняю данные по операциям в файл

    file = f'/Volumes/big4photo/Documents/Инвестиции/API_data/{filename_data}/operations_{account_name}_{filename_data}.csv'
    df = pd.read_csv(file)

    only_real_bonds = df.query('instrument_type == "Bond" and  status == "Done"') \
        [['figi', 'operation_type', 'payment', 'quantity_executed']]  # датафрэйм с куплеными облигациями есть предположение , что quantity на до заменить на quantity_executed

    real_bonds_with_name = bonds_name.merge(only_real_bonds, on='figi')[
        ['name', 'ticker', 'figi', 'operation_type', 'payment', 'quantity_executed']]
    # датафрэйм со всей необхоимой информацией об облигациях и именами

    real_bonds_with_name.to_excel(
        f'/Volumes/big4photo/Documents/Инвестиции/API_data/{filename_data}/bonds_on_{account_name}_{filename_data}.xlsx',
        index=False)

    # сохраняю файлы портфолио
    get_portfolio(client, account_id[account_name]).to_csv(
        f'/Volumes/big4photo/Documents/Инвестиции/API_data/{filename_data}/portfolio_{account_name}_{filename_data}.csv',
        index=False)

    # добавляю фрагмент для проверки валюты на счетах

    work_file = f'{csv_file_path}/{file_name}_{account_name}.csv'
    currensy_list = currency_report(client, account_id[account_name])

    if os.path.exists(work_file):
        write_csv(currensy_list, filename_data, work_file)
    else:
        create_csv(work_file)
        write_csv(currensy_list, filename_data, work_file)

    subprocess.call(['open', work_file])
