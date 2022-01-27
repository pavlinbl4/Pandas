"""
20220116 скрипт обращается к ранее созданным файлам с помощью new_super_script
и создает в папке дня файл с отчетом по результатам выплаты купонов по облигациям

если возникает ошибка
Traceback (most recent call last):
  File "/Volumes/big4photo/_PYTHON/Pandas/Invest/with_pandas/get_bonds_rezult.py", line 76, in <module>
    tickers_data[7] = round(itog_df.ClearIncome.sum(), 2)
TypeError: type str doesn't define __round__ method
 то значит данный файл уже существует
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

columns_names = ['Name', 'Tiсker', 'Quantity', 'Coupon', 'Buy', 'BrokerCommission', 'PartRepayment', 'TaxCoupon', 'Sell',
                         'BuyCard', 'ClearIncome', 'Final','Min_sale_price']


def write_to_csv(filename_data, API_folder, tickers_data):  # запись в csv файл данных по каждому тикеру
    with open(f'{API_folder}/{filename_data}/bonds_rezult_{filename_data}.csv', 'a') as input_file:
        writer = csv.writer(input_file)
        writer.writerow(tickers_data)


def ticker_report(my_ticker, bonds_df):  # результаты по тикеру из единного датафрэйма
    bonds_name = bonds_df[bonds_df.ticker == my_ticker].name.unique()[0]
    coupon = bonds_df[bonds_df.ticker == my_ticker].query('operation_type == "Coupon"').payment.sum().round(2)
    buy = bonds_df[bonds_df.ticker == my_ticker].query('operation_type == "Buy"').payment.sum().round(2)
    broker_commission = bonds_df[bonds_df.ticker == my_ticker].query(
        'operation_type == "BrokerCommission"').payment.sum().round(2)
    part_repayment = bonds_df[bonds_df.ticker == my_ticker].query('operation_type == "PartRepayment"').payment.sum()
    tax_coupon = bonds_df[bonds_df.ticker == my_ticker].query('operation_type == "TaxCoupon"').payment.sum()
    sell = bonds_df[bonds_df.ticker == my_ticker].query('operation_type == "Sell"').payment.sum()
    buy_card = bonds_df[bonds_df.ticker == my_ticker].query('operation_type == "BuyCard"').payment.sum().round(2)

    clear_income = round(coupon + broker_commission + tax_coupon + buy_card, 2)
    final = round(coupon + buy + broker_commission + part_repayment + tax_coupon + sell + buy_card, 2)
    # print(bonds_df[bonds_df.ticker == my_ticker].query('operation_type == "Buy"'))



    bonds_quantity = bonds_df.query('quantity > 0') \
        .groupby('ticker', as_index=False).sum() \
        .query("ticker == @my_ticker") \
        .quantity \
        .values[0]                      # количество купленных облигций

    min_sale_price = round(abs(final + broker_commission) / bonds_quantity, 3) # минимальная цена продажи бумаги



    tickers_data = [bonds_name, my_ticker,bonds_quantity, coupon, buy, broker_commission, part_repayment, tax_coupon, sell, buy_card,
                    clear_income, final, min_sale_price]
    write_to_csv(filename_data, API_folder, tickers_data)


def create_tickers_set(bonds_df):
    return set(bonds_df.ticker.unique())  # список тикеров облигаций


def create_file(API_folder,filename_data,columns_names):# создаю csv файл с заголовками таблицы
    with open(f'{API_folder}/{filename_data}/bonds_rezult_{filename_data}.csv',
              'w') as input_file:
        writer = csv.writer(input_file)
        writer.writerow(columns_names)

create_file(API_folder,filename_data,columns_names)

for account_name in account_id:
    # по каждому аккаунту считываю файл сегодняшнего дня по облигациям и создаю единный датафрэйм
    df = pd.read_excel(f'{API_folder}/{filename_data}/bonds_on_{account_name}_{filename_data}.xlsx')
    bonds_df = bonds_df.append(df)

    all_tickers = create_tickers_set(bonds_df)  # вызываю функцию создающию коллекцию тикеров моих облигаций
print(bonds_df.columns)

for my_ticker in all_tickers:  # прохожусь циклом по коллекции тикеров и формирую отчет по каждому
    ticker_report(my_ticker, bonds_df)

itog_df = pd.read_csv(
    f'{API_folder}/{filename_data}/bonds_rezult_{filename_data}.csv')  # cчитываю датафрэйм из созданной таблицы

# itog_df = itog_df.sort_values(by=['Buy'])
# print(itog_df)

# itog_df.to_csv(f'{API_folder}/{filename_data}/bonds_rezult_{filename_data}.csv')



tickers_data = [None] * len(columns_names)

for i in range(3,len(columns_names)):
    tickers_data[i] = itog_df[columns_names[i]].sum().round(2)

write_to_csv(filename_data, API_folder, tickers_data)



subprocess.call(['open', f'{API_folder}/{filename_data}/bonds_rezult_{filename_data}.csv'])
