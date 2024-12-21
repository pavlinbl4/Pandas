"""
Данный скрипт извлекает только нужные данные о
проданных фотоснимках их xlsx файла отчета
и выводит лучший снимок и лучшего покупателя
"""
from pathlib import Path

import pandas as pd
from colorama import Fore, init, Style

from download_tass_preview import download_photo_preview_by_id

init()
# преобразование таблицы отчета в датафрейм с удалением ненужной информации
def read_table_from_excel(file_path: str) -> object:
    # Читаем весь файл
    xl = pd.ExcelFile(file_path)

    # Читаем первый лист
    df = xl.parse(0, header=None)

    # Находим индекс первой строки, где в первой колонке стоит 1
    start_index = df.index[df[0] == '1'][0]

    # находим период отчета
    period_index = df.index[df[1].str.strip() == 'Период:'][0]
    period = df.iloc[period_index][2]

    # Находим индекс последней строки
    end_index = df.index[df[0] == 'Итого доход от использования фотоснимков:'][0] - 1

    # Читаем только нужные строки
    df = xl.parse(0, header=start_index - 1, nrows=end_index - start_index + 1)

    # Берем данные только из нужных колонок
    columns_to_select = ['ID фото',
                         'Компания',
                         'Доход от использования фотоснимков в рублях (с НДС), руб.', ]
    df = df[columns_to_select]

    # переименовываем колонки
    df = df.rename(columns={'ID фото': 'photo_id',
                            'Компания': 'company',
                            'Доход от использования фотоснимков в рублях (с НДС), руб.': 'income'})

    # устанавливаем тип данных для 'photo_id'
    df = convert_data_to_string('photo_id', df)

    # устанавливаем тип данных для 'income'
    df = convert_digits_with_comma_to_float('income', df)

    # возвращаю дата фрейм с тремя колонками и правильным типом данных и датой периода отчета
    return df, period


def convert_data_to_string(column_name, df):
    df[column_name] = df[column_name].astype(str)
    return df


def convert_digits_with_comma_to_float(column_name, df):
    df[column_name] = df[column_name].astype(str)  # Преобразование всех значений в строки
    df[column_name] = df[column_name].str.replace('\xa0', ' ')
    df[column_name] = df[column_name].str.replace(',', '.')
    df[column_name] = df[column_name].str.replace(' ', '')
    df[column_name] = df[column_name].astype(float)
    return df


def find_bestseller(df, research_column_name, income_column_name='income'):
    # находим уникальные значения в заданной колонке и суммируем доход для данной выборки
    # в данном случае это может быть либо photo_id, либо company
    unique_image_df = (df.groupby(research_column_name)[income_column_name]
                       .sum().reset_index())

    # Находим строку с максимальной ценой
    max_sale_row = unique_image_df.loc[unique_image_df[income_column_name].idxmax()]

    # находим данные в искомой колонке, где максимальная продажа (либо photo_id, либо company)
    best_sell = max_sale_row[research_column_name]

    # определяем величину максимальной продажи
    max_sale_income = unique_image_df[income_column_name].max()
    max_sale_income = round(max_sale_income, 2)

    # находим количество упоминаний объекта для максимальной продаже
    sold_count_for_best_image = df[research_column_name].value_counts()[best_sell]

    return best_sell, sold_count_for_best_image, max_sale_income,


def best_in_month(df, research_column_name):
    bestseller = find_bestseller(df,
                                 research_column_name,
                                 'income'
                                 )
    return bestseller


def expensive_image(df):
    expensive_image_income = df['income'].max()

    expensive_image_id = df.loc[df['income'].idxmax(), 'photo_id']

    return expensive_image_income, expensive_image_id


def main(path_to_report_xlsx_file_):
    # преобразую xlsx файл в рабочий датафрейм
    df, period = read_table_from_excel(path_to_report_xlsx_file_)

    best_photo_id_, sold_count_for_best_image_, max_sale_income_ = (
        best_in_month(df, 'photo_id'))

    print(Fore.RED + Style.DIM + f" Период {period}" + Fore.RESET + '\n\n',
          Fore.GREEN + f"лучшее фото месяца {best_photo_id_}\n" + Fore.RESET,
          f" продано {sold_count_for_best_image_} раз\n"
          f" на сумму  {max_sale_income_}\n")

    customer_, sold_count_for_best_image_, max_sale_income_ = (
        best_in_month(df, 'company'))

    print(Fore.GREEN + f" Лучший покупатель месяца {customer_}\n" + Fore.RESET,
          f" продано {sold_count_for_best_image_} раз\n"
          f" на сумму  {max_sale_income_}\n")

    expensive_image_income, expensive_image_id = expensive_image(df)

    print(Fore.GREEN + f" Самый дорогой снимок {expensive_image_id}\n" + Fore.RESET,
          f" куплен за  {expensive_image_income}\n"
          )

    download_photo_preview_by_id(expensive_image_id, 'Expensive_image',
                                 image_file_name=f'{period}_Expensive_image_{expensive_image_id}_sold_price-{expensive_image_income}.JPG')

    download_photo_preview_by_id(best_photo_id_, 'Best_sellers',
                                 image_file_name=f'{period}_Best_photo_{best_photo_id_}_sold_price-{max_sale_income_}.JPG')


if __name__ == '__main__':

    icloud_folder = Path().home() / 'Library/Mobile Documents/com~apple~CloudDocs/'

    for report_xlsx_file in (Path().home() / f'{icloud_folder}/TASS/original_reports/').iterdir():
        if Path(report_xlsx_file).suffix == '.xlsx':

            main(report_xlsx_file)
    # path_to_report_xlsx_file = filedialog.askopenfile().name
    # main(path_to_report_xlsx_file)
