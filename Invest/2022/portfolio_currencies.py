# сохраняю отчеты по остаткам валюты на брокерских счетах

from tf_invest_token import token_tf, account_id
import tinvest
import datetime
import csv
import os.path

TOKEN = token_tf
client = tinvest.SyncClient(TOKEN)
account_id = account_id

filename_data = datetime.date.today()
csv_file_path = '/Volumes/big4photo/Documents/Инвестиции'
file_name = "Валюта_на_счете"


def create_csv(work_file):  # создаю файл отчета - одноразовая операция
    with open(work_file, 'a') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(('Дата', 'EUR', 'RUB', 'USD'))


def write_csv(data, filename_data, work_file):  # записвваю данные в файл отчета  для каждого счета
    with open(work_file, 'a') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow((filename_data, data[0].balance, data[1].balance, data[2].balance))


def currency_report(client, account):  # получаю список с данными по валютам на счете
    return client.get_portfolio_currencies(broker_account_id=account).payload.currencies


for account_name in account_id:  # прохожусь по словарю содержащему аккаунты счетов и для каждого дополняю отчет
    work_file = f'{csv_file_path}/{file_name}_{account_name}.csv'
    currensy_list = currency_report(client, account_id[account_name])
    if os.path.exists(work_file):
        write_csv(currensy_list, filename_data, work_file)
    else:
        create_csv(work_file)
        write_csv(currensy_list, filename_data, work_file)

# print(response) # получаю ответ от API , далее беру , то что слева от знака равно "payload"
# print("*"*150)
# print(response.payload) # снова добавляю. то что слева от знака равно  "currencies"
# print("*"*150)
# print(response.payload.currencies) # в итоге получаю список валют
# print("*"*150)
# print(response.payload.currencies[1].currency)
# print(response.payload.currencies[1].blocked)
# print(response.payload.currencies[1].balance)
