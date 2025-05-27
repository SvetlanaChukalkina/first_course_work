from typing import Any

import datetime
import json
import logging
import os

import pandas as pd
import requests
from dotenv import load_dotenv

from config import PATH_XLSX, USER_SETTINGS

load_dotenv()

API_KEY = os.getenv("API_KEY")

utils_logger = logging.getLogger()
utils_file_handler = logging.FileHandler("logs/logs.log", "w")
utils_file_formatter = logging.Formatter("%(asctime)s %(filename)s %(levelname)s: %(message)s")
utils_file_handler.setFormatter(utils_file_formatter)
utils_logger.addHandler(utils_file_handler)
utils_logger.setLevel(logging.DEBUG)


def excel_reader(path: str = PATH_XLSX) -> pd.DataFrame:
    """Cчитывает данные из Excel-файла, возвращает датафрейм"""
    try:
        excel_data = pd.read_excel(path)
        utils_logger.info("Processing was successful")
        return excel_data
    except FileNotFoundError as err:
        utils_logger.error("File not found")
        raise err


def date_replace(from_date: datetime.datetime, param):
    """Преобразовывает дату в соответствии с выбранным пользователем параметром"""
    if param == "W":
        utils_logger.info("Selected interval: from beginning of the week")
        return from_date - datetime.timedelta(from_date.weekday())
    elif param == "M":
        utils_logger.info("Selected interval: from beginning of the month")
        return datetime.datetime(from_date.year, from_date.month, 1)
    elif param == "Y":
        utils_logger.info("Selected interval: from beginning of the year")
        return datetime.datetime(from_date.year, 1, 1)
    elif param == "ALL":
        utils_logger.info("Selected interval: from beginning of the 2000th year")
        return datetime.datetime(2000, 1, 1)
    else:
        utils_logger.error("The wrong parameter is selected")
        return "Выбран неверный параметр"


def filter_operations(param, to_date, df = excel_reader()):
    """Отбирает операции, соответствующие выбранному периоду"""
    to_date_formatted = datetime.datetime.strptime(to_date, "%d.%m.%Y")
    from_date_formatted = date_replace(to_date_formatted, param)
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True)
    df_for_date = df[(df["Дата операции"] <= to_date_formatted) & (df["Дата операции"] >= from_date_formatted)]
    utils_logger.info("Operations are filtered by the selected interval")
    return df_for_date


def data_expences(df_data: pd.DataFrame):
    """Выводит общую сумму расходов, топ-7 категорий по сумме расходов,
    отдельно выводит расходы по категориям 'Наличные' и 'Переводы',
    суммирует расходы по категориям, не входящим в топ-7, в категорию 'Остальное'"""
    total_expences_dict = {"total_amount": 0, "main": [], "transfers_and_cash": []}
    others_sum = 0
    expences_categories_df = df_data.groupby("Категория", dropna=True).agg({"Сумма операции": "sum"}).abs()
    sum_cash_and_transfers = (
        df_data[(df_data["Категория"] == "Наличные") | (df_data["Категория"] == "Переводы")]
        .groupby("Категория", dropna=True)
        .agg({"Сумма операции": "sum"})
        .abs()
    )
    sorted_sum = expences_categories_df.sort_values(by="Сумма операции", ascending=False)
    top_seven_categories, other_categories = sorted_sum[:7], sorted_sum[7:]
    for category, description in sorted_sum.iterrows():
        total_expences_dict["total_amount"] += int(description["Сумма операции"])
    for top_category, top_description in top_seven_categories.iterrows():
        total_expences_dict["main"].append(
            {
                "category": "Без категории" if not top_category else top_category,
                "amount": int(top_description["Сумма операции"]),
            }
        )
    for other_category, other_description in other_categories.iterrows():
        others_sum += int(other_description["Сумма операции"])

    for cash, transfer in sum_cash_and_transfers.iterrows():
        total_expences_dict["transfers_and_cash"].append({"category": cash, "amount": int(transfer["Сумма операции"])})

    total_expences_dict["main"].append({"category": "Остальное", "amount": others_sum})
    utils_logger.info("Block data_expences is full")
    return total_expences_dict


def data_income(income_df_data: pd.DataFrame):
    """Рассчитывает сумму поступлений на счет (положительное изменение суммы)"""
    data = {"total_amount": 0, "main": []}
    income_df = (
        income_df_data[income_df_data["Сумма операции"] > 0]
        .groupby("Категория", dropna=True)
        .agg({"Сумма операции": "sum"})
        .abs()
    )
    for income_category, income_description in income_df.iterrows():
        data["total_amount"] += int(income_description["Сумма операции"])
        data["main"].append({"category": income_category, "amount": int(income_description["Сумма операции"])})
    utils_logger.info("Block data_income is full")
    return data


def convert(symbol) -> Any:
    """Обращается к внешнему API для получения курса валют и конвертации суммы в рубли"""
    url = "https://api.twelvedata.com/exchange_rate"
    payload = {"symbol": symbol, "apikey": API_KEY}
    response = requests.get(url, params=payload)
    status_code = response.status_code
    if status_code == 200:
        utils_logger.info("API-request was completed successfully")
        response_data = response.json()
        return response_data.get("rate")
    else:
        utils_logger.error("Request error")
        raise Exception("Ошибка запроса")


def stocks_api(symbol):
    """Обращается к внешнему API для получения стомости акций"""
    url = "https://api.twelvedata.com/price"
    payload = {"symbol": symbol, "apikey": API_KEY}
    response = requests.get(url, params=payload)
    status_code = response.status_code
    if status_code == 200:
        utils_logger.info("API-request was completed successfully")
        data = response.json()
        get_data = data.get("price")
        return get_data
    else:
        utils_logger.error("Request error")
        raise Exception("Ошибка запроса")


def read_user_settings():
    """Функция чтения пользовательского файла с наименованиями
    валют и акций"""
    try:
        with open(USER_SETTINGS) as json_f:
            utils_logger.info("File has been converted")
            return json.load(json_f)
    except Exception as err:
        utils_logger.error("Reading error")
        raise err


def iter_user_settings(user_file=read_user_settings()):
    """Извлекает наименования валют и акций из пользовательского файла
    для использования в функциях с API-запросами"""
    user_currencies = user_file["user_currencies"]
    user_stocks = user_file["user_stocks"]
    currency_rates = []
    stocks_convert = []
    for currency in user_currencies:
        convert_currency = convert(f"{currency}/RUB")
        currency_rates.append({"currency": currency, "rate": convert_currency})
    for stock in user_stocks:
        convert_stocks = stocks_api(stock)
        stocks_convert.append({"stock": stock, "price": convert_stocks})

    return currency_rates, stocks_convert
