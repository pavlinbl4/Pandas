"""
20220116 скрипт обращается к ранее созданным файлам с помощью new_super_script
и создает в папке дня файл с отчетом по результатам выплаты купонов по облигациям
"""

from tf_invest_token import token_tf
import pandas as pd
import datetime
import tinvest
import csv
import subprocess

today_data = datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()
filename_data = datetime.date.today()
API_folder = '/Volumes/big4photo/Documents/Инвестиции/API_data'

TOKEN = token_tf
client = tinvest.SyncClient(TOKEN)

client = tinvest.SyncClient(TOKEN)

accounts_info = client.get_accounts().payload.accounts  # получаю данные по аккаунта
df = pd.DataFrame([s.dict() for s in accounts_info])  # датафрэйм с данными аккаунта
account_id = {'iis': int(df.broker_account_id[1]), 'broker': int(df.broker_account_id[0])}  # словарь с данными аккаунта

bonds_df = pd.DataFrame()  # создаю пустой единый датафрэйм


def write_to_csv(filename_data, API_folder, tickers_data):  # запись в csv файл данных по каждому тикеру
    with open(f'{API_folder}/{filename_data}/bonds_rezult_{filename_data}.csv', 'a') as input_file:
        writer = csv.writer(input_file)
        writer.writerow(tickers_data)


def ticker_report(my_ticker, bonds_df):  # результаты по тикеру из единного датафрэйма
    bonds_name = bonds_df[bonds_df.ticker == my_ticker].name.unique()[0]
    buy = bonds_df[bonds_df.ticker == my_ticker].query('operation_type == "Buy"').payment.sum().round(2)
    buy_card = bonds_df[bonds_df.ticker == my_ticker].query('operation_type == "BuyCard"').payment.sum().round(2)
    tax_coupon = bonds_df[bonds_df.ticker == my_ticker].query('operation_type == "TaxCoupon"').payment.sum()
    coupon = bonds_df[bonds_df.ticker == my_ticker].query('operation_type == "Coupon"').payment.sum().round(2)
    broker_commission = bonds_df[bonds_df.ticker == my_ticker].query(
        'operation_type == "BrokerCommission"').payment.sum().round(2)
    clear_income = round(coupon + broker_commission + tax_coupon + buy_card, 2)

    tickers_data = [bonds_name, my_ticker, coupon, buy, buy_card, tax_coupon, broker_commission, clear_income]
    write_to_csv(filename_data, API_folder, tickers_data)


def create_tickers_set(bonds_df):
    return set(bonds_df.ticker.unique())  # список тикеров облигаций


with open(f'{API_folder}/{filename_data}/bonds_rezult_{filename_data}.csv',
          'a') as input_file:  # создаю csv  файл с заголовками таблицы
    columns_names = ['Name', 'Tiker', 'Payed_Coupons', 'Buy', 'BuyCard', 'TaxCoupon', 'BrokerCommission', 'ClearIncome']
    writer = csv.writer(input_file)
    writer.writerow(columns_names)

for account_name in account_id:
    # по каждому аккаунту считываю файл сегодняшнего дня по облигациям и создаю единный датафрэйм
    df = pd.read_excel(f'{API_folder}/{filename_data}/bonds_on_{account_name}_{filename_data}.xlsx')
    bonds_df = bonds_df.append(df)
    all_tickers = create_tickers_set(bonds_df)  # вызываю функцию создающию коллекцию тикеров моих облигаций

for my_ticker in all_tickers:  # прохожусь циклом по коллекции тикеров и формирую отчет по каждому
    ticker_report(my_ticker, bonds_df)



itog_df = pd.read_csv(f'{API_folder}/{filename_data}/bonds_rezult_{filename_data}.csv',
                      usecols=['ClearIncome'])  # считаю чистый доход по купонам

tickers_data = [None] * 8
tickers_data[7] = round(itog_df.ClearIncome.sum(), 2)
write_to_csv(filename_data, API_folder, tickers_data)

subprocess.call(['open', f'{API_folder}/{filename_data}/bonds_rezult_{filename_data}.csv'])
