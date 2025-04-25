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


def excel_reader(path: str) -> pd.DataFrame:
    """Cчитывает данные из Excel-файла"""
    try:
        excel_data = pd.read_excel(path)
        return excel_data
    except FileNotFoundError as err:
        raise err


def json_reader(path: str):
    """Cчитывает данные из JSON-файла"""
    with open(path, 'r', encoding="utf-8") as json_file:
        return json.load(json_file)


def date_replace(from_date: datetime.datetime, param):

    if param == "W":
        return from_date - datetime.timedelta(from_date.weekday())
    elif param == "M":
        return datetime.datetime(from_date.year, from_date.month, 1)
    elif param == "Y":
        return datetime.datetime(from_date.year, 1, 1)
    elif param == "ALL":
        return datetime.datetime(2000, 1, 1)


def method_name(param, to_date):
    df = excel_reader(path="data/operations.xlsx")
    # Запрос дат
    from_date = datetime.datetime.strptime(to_date, '%d.%m.%Y')
    start_date = date_replace(from_date, param)
    df['Дата операции'] = pd.to_datetime(df['Дата операции'], dayfirst=True)
    df_for_date = df[(df['Дата операции'] <= from_date) & (df['Дата операции'] >= start_date)]
    return df_for_date


def data_expences(df: pd.DataFrame):
    """Выводит топ-7 категорий по сумме расходов"""
    total_dict = {"total_amount": 0, "main": [], "transfers_and_cash": []}
    sum_ostalnie = 0
    # df = df.fillna("")
    out_categories_df = df.groupby("Категория", dropna=True).agg({"Сумма операции": "sum"}).abs()
    cash_transfers = df[(df["Категория"] == "Наличные") | (df["Категория"] == "Переводы")].groupby("Категория",
                                                                                                   dropna=True).agg(
        {"Сумма операции": "sum"}).abs()

    sorted_sum = out_categories_df.sort_values(by="Сумма операции", ascending=False)
    top_seven, not_top_seven = sorted_sum[:7], sorted_sum[7:]
    for out, cat in sorted_sum.iterrows():
        total_dict["total_amount"] += int(cat["Сумма операции"])

    for top, sev in top_seven.iterrows():
        total_dict["main"].append(
            {"category": "Без категории" if not top else top, "amount": int(sev["Сумма операции"])})

    for not_top, not_sev in not_top_seven.iterrows():
        sum_ostalnie += int(not_sev["Сумма операции"])

    for cash, transfer in cash_transfers.iterrows():
        total_dict["transfers_and_cash"].append({"category": cash, "amount": int(transfer["Сумма операции"])})

    total_dict["main"].append({"category": "Остальное", "amount": sum_ostalnie})

    return total_dict


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


def convert(symbol:str, amount:int) -> Any:
    """Обращается к внешнему API для получения курса валют и конвертации суммы в рубли"""
    url = "https://www.alphavantage.co/query"
    payload = {"function": "TIME_SERIES_WEEKLY", "symbol": symbol, "amount": amount, "apikey": API_KEY}
    response = requests.get(url, params=payload)

    status_code = response.status_code
    if status_code == 200:
        resp_data = response.json()
        super_data = resp_data["Weekly Time Series"]
        index_key = list(super_data.keys())[0]
        return super_data[index_key]["2. high"]
    else:
        raise Exception("Ошибка запроса")
print(convert(symbol="USD", amount=100))

    #     super_data = resp_data["Weekly Time Series"]
    #     index_key = list(super_data.keys())[0]
    #     return super_data[index_key]["2. high"]
    # else:
    #     raise Exception("Ошибка запроса")


def read_user_settings():
    try:
        with open(USER_SETTINGS) as json_f:
            return json.load(json_f)
    except Exception as err:
        raise err


def stocks_api(symbol):

    url = "https://www.alphavantage.co/query"
    payload = {"function": "GLOBAL_QUOTE", "symbol": symbol}
    response = requests.get(url, params=payload)

    status_code = response.status_code
    if status_code == 200:
        data = response.json()
        # print(data)
        get_data = data.get("Global Quote", {}).get("05. price", 0)
        return float(get_data)
    else:
        raise Exception("Ошибка запроса")

def iter_user_settings():
    user_file = read_user_settings()
    user_currencies = user_file["user_currencies"]
    user_stocks = user_file["user_stocks"]
    currency_rates = []
    stocks_convert = []
    for currency in user_currencies:
        convert_currency = convert(currency, amount=10)
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


