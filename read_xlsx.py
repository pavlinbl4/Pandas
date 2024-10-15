"""
Данный скрипт извлекает только нужные данные о
проданных фотоснимках их xlsx файла отчета
и выводит лучший снимок и лучшего покупателя
"""

import pandas as pd


def read_table_from_excel(file_path: str) -> object:
    # Читаем весь файл
    xl = pd.ExcelFile(file_path)

    # Читаем первый лист
    df = xl.parse(0, header=None)

    # Находим индекс первой строки, где в первой колонке стоит 1
    start_index = df.index[df[0] == '1'][0]

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

    # возвращаю дата фрейм с тремя колонками и правильным типом данных
    return df


def convert_data_to_string(column_name, df):
    df[column_name] = df[column_name].astype(str)
    return df


def convert_digits_with_comma_to_float(column_name, df):
    df[column_name] = df[column_name].str.replace('\xa0', ' ')
    df[column_name] = df[column_name].str.replace(',', '.')
    df[column_name] = df[column_name].str.replace(' ', '')
    df[column_name] = df[column_name].astype(float)
    return df


def find_bestseller(df, research_column_name, income_column_name='income'):
    # находим уникальные значения в заданной колонке и суммируем доход для данной выборки
    unique_image_df = (df.groupby(research_column_name)[income_column_name]
                       .sum().reset_index())

    # Находим строку с максимальной ценой
    max_sale_row = unique_image_df.loc[unique_image_df[income_column_name].idxmax()]

    # находим данные в искомой колонке, где максимальная продажа
    best_sell = max_sale_row[research_column_name]

    # определяем величину максимальной продажи
    max_sale_income = unique_image_df[income_column_name].max()

    # находим количество упоминаний объекта для максимальной продаже
    sold_count_for_best_image = df[research_column_name].value_counts()[best_sell]

    return best_sell, sold_count_for_best_image, max_sale_income


def best_in_month(path_to_report_xlsx_file, research_column_name):
    # преобразую xlsx файл в рабочий дата фрейм
    df = read_table_from_excel(
        path_to_report_xlsx_file)

    bestseller = find_bestseller(df,
                                 research_column_name,
                                 'income'
                                 )

    return bestseller


if __name__ == '__main__':
    path_to_report_xlsx_file_ = \
        '/Users/evgeniy/Downloads/Валентинович. Отчет для ФЛ  от 09.10.2024.xlsx'
    # '/Users/evgeniy/Downloads/Павленко Евгений Валентинович. Отчет для ФЛ от 08.08.2024.xlsx'

    best_photo_id_, sold_count_for_best_image_, max_sale_income_ = (
        best_in_month(path_to_report_xlsx_file_, 'photo_id'))

    print(f" Лучшее фото месяца {best_photo_id_}\n"
          f" продано {sold_count_for_best_image_} раз\n"
          f" на сумму  {max_sale_income_}\n")

    customer_, sold_count_for_best_image_, max_sale_income_ = (
        best_in_month(path_to_report_xlsx_file_, 'company'))

    print(f" Лучший покупатель месяца {customer_}\n"
          f" продано {sold_count_for_best_image_} раз\n"
          f" на сумму  {max_sale_income_}\n")
