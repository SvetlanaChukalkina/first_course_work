import datetime
import os
import requests
import pandas as pd
import json
from dotenv import load_dotenv

from config import USER_SETTINGS

load_dotenv()
from typing import Any

API_KEY = os.getenv("API_KEY")


def excel_reader(path:str="../data/operations.xlsx") -> pd.DataFrame:
    """Cчитывает данные из Excel-файла, возвращает датафрейм"""
    try:
        excel_data = pd.read_excel(path)
        return excel_data
    except FileNotFoundError as err:
        raise err


def json_reader(path: str) -> None:
    """Cчитывает данные из JSON-файла"""
    with open(path, 'r', encoding="utf-8") as json_file:
        return json.load(json_file)


def date_replace(from_date: datetime.datetime, param):
    """Преобразовывает дату в соответствии с выбранным пользователем параметром"""
    while True:
        if param == "W":
            return from_date - datetime.timedelta(from_date.weekday())
            break
        elif param == "M":
            return datetime.datetime(from_date.year, from_date.month, 1)
            break
        elif param == "Y":
            return datetime.datetime(from_date.year, 1, 1)
            break
        elif param == "ALL":
            return datetime.datetime(2000, 1, 1)
            break
        else:
            print("Введите один из предложенных параметров")


def filter_operations(param, to_date):
    """Отбирает операции, соответствующие выбранному периоду"""
    df = excel_reader(path="data/operations.xlsx")
    from_date = datetime.datetime.strptime(to_date, '%d.%m.%Y')
    from_date_formatted = date_replace(from_date, param)
    df['Дата операции'] = pd.to_datetime(df['Дата операции'], dayfirst=True)
    df_for_date = df[(df['Дата операции'] <= from_date) & (df['Дата операции'] >= from_date_formatted)]
    return df_for_date


def data_expences(df: pd.DataFrame):
    """Выводит общую сумму расходов, топ-7 категорий по сумме расходов,
    отдельно выводит расходы по категориям 'Наличные' и 'Переводы',
    суммирует расходы по категориям, не входящим в топ-7, в категорию 'Остальное' """
    total_expences_dict = {"total_amount": 0, "main": [], "transfers_and_cash": []}
    others_sum = 0
    expences_categories_df = df.groupby("Категория", dropna=True).agg({"Сумма операции": "sum"}).abs()
    sum_cash_and_transfers = df[(df["Категория"] == "Наличные") | (df["Категория"] == "Переводы")].groupby("Категория",
                                                                                                           dropna=True).agg(
        {"Сумма операции": "sum"}).abs()
    sorted_sum = expences_categories_df.sort_values(by="Сумма операции", ascending=False)
    top_seven_categories, others_categories = sorted_sum[:7], sorted_sum[7:]
    for out, cat in sorted_sum.iterrows():
        total_expences_dict["total_amount"] += int(cat["Сумма операции"])
    for top, sev in top_seven_categories.iterrows():
        total_expences_dict["main"].append(
            {"category": "Без категории" if not top else top, "amount": int(sev["Сумма операции"])})
    for not_top, not_sev in others_categories.iterrows():
        others_sum += int(not_sev["Сумма операции"])

    for cash, transfer in sum_cash_and_transfers.iterrows():
        total_expences_dict["transfers_and_cash"].append({"category": cash, "amount": int(transfer["Сумма операции"])})

    total_expences_dict["main"].append({"category": "Остальное", "amount": others_sum})

    return total_expences_dict


def data_income(df: pd.DataFrame):
    data = {
        "total_amount": 0,
        "main": []
    }
    income_df = df[df["Сумма операции"] > 0].groupby("Категория", dropna=True).agg({"Сумма операции": "sum"}).abs()
    for icat, come in income_df.iterrows():
        data["total_amount"] += int(come["Сумма операции"])
        data["main"].append({"category": icat, "amount": int(come["Сумма операции"])})
    return data


def convert(symbol) -> Any:
    """Обращается к внешнему API для получения курса валют и конвертации суммы в рубли"""
    url = "https://api.twelvedata.com/exchange_rate"
    payload = {"symbol": symbol, "apikey": API_KEY}
    response = requests.get(url, params=payload)
    status_code = response.status_code
    if status_code == 200:
        resp_data = response.json()
        super_data = resp_data
        return super_data.get("rate")
    else:
        raise Exception("Ошибка запроса")


def read_user_settings():
    try:
        with open(USER_SETTINGS) as json_f:
            return json.load(json_f)
    except Exception as err:
        raise err


def stocks_api(symbol):

    url = "https://api.twelvedata.com/price"
    payload = {"symbol": symbol, "apikey": API_KEY}
    response = requests.get(url, params=payload)

    status_code = response.status_code
    if status_code == 200:
        data = response.json()
        get_data = data.get('price')
        return get_data
    else:
        raise Exception("Ошибка запроса")

def iter_user_settings():
    user_file = read_user_settings()
    user_currencies = user_file["user_currencies"]
    user_stocks = user_file["user_stocks"]
    currency_rates = []
    stocks_convert = []
    for currency in user_currencies:
        convert_currency = convert(f"{currency}/RUB")
        currency_rates.append({
        "currency": currency,
        "rate": convert_currency
    })
    for stock in user_stocks:
        convert_stocks = stocks_api(stock)
        stocks_convert.append({
            "stock": stock,
            "price": convert_stocks
        })

    return currency_rates, stocks_convert
print(iter_user_settings())
