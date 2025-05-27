import datetime
from logging import raiseExceptions
from typing import Any
from unittest.mock import patch, mock_open

import pandas as pd
import pytest

from src.utils import (
    convert,
    data_expences,
    data_income,
    date_replace,
    excel_reader,
    filter_operations,
    iter_user_settings,
    stocks_api,
)

def test_no_excel_reader():
    with pytest.raises(FileNotFoundError):
        excel_reader(path="ggjh")


@pytest.mark.parametrize(
    "value, param,expected",
    [
        (datetime.datetime.strptime("20.10.2020", "%d.%m.%Y"), "W", datetime.datetime(2020, 10, 19, 0, 0)),
        (datetime.datetime.strptime("20.10.2020", "%d.%m.%Y"), "M", datetime.datetime(2020, 10, 1, 0, 0)),
        (datetime.datetime.strptime("20.10.2020", "%d.%m.%Y"), "Y", datetime.datetime(2020, 1, 1, 0, 0)),
        (datetime.datetime.strptime("20.10.2020", "%d.%m.%Y"), "ALL", datetime.datetime(2000, 1, 1, 0, 0)),
    ],
)
def test_date_replace(value, param, expected) -> None:
    """Проверка корректности работы функции date_replace с разными входными данными"""
    assert date_replace(value, param) == expected


def test_data_expences(test_dataframe):
    """Проверка корректности работы функции data_expences"""
    assert data_expences(df_data=test_dataframe) == {
        "total_amount": 138630,
        "main": [
            {"category": "Зарплата", "amount": 93000},
            {"category": "Путешествия", "amount": 20000},
            {"category": "Развлечения", "amount": 7000},
            {"category": "Рестораны", "amount": 4500},
            {"category": "Красота", "amount": 3500},
            {"category": "Продукты", "amount": 2430},
            {"category": "Наличные", "amount": 2000},
            {"category": "Остальное", "amount": 6200},
        ],
        "transfers_and_cash": [{"category": "Наличные", "amount": 2000}],
    }


def test_data_income(test_dataframe):
    """Проверка корректности работы функции data_income"""
    assert data_income(income_df_data=test_dataframe) == {
        "total_amount": 99500,
        "main": [
            {"category": "Бонусы", "amount": 350},
            {"category": "Зарплата", "amount": 93000},
            {"category": "Наличные", "amount": 2000},
            {"category": "Перевод", "amount": 4150},
        ],
    }


@patch("requests.get")
def test_convert(convert_mock: Any):
    """Проверка работы функции convert без необходимости обращения к внешнему API"""

    convert_mock.return_value.status_code = 200
    convert_mock.return_value.json.return_value = {"rate": 57}
    result = convert("EUR")
    assert result == 57


@patch("requests.get")
def test_stocks_api(stocks_mock: Any):
    stocks_mock.return_value.status_code = 200
    stocks_mock.return_value.json.return_value = {"price": 100}
    result = stocks_api("TSLA")
    assert result == 100


@patch("src.utils.convert")
@patch("src.utils.stocks_api")
def test_iter_user_settings(stocks_mock, convert_mock):
    stocks_mock.return_value = 157
    convert_mock.return_value = 200
    result = iter_user_settings({"user_currencies": ["USD"], "user_stocks": ["AAPL"]})
    assert result == ([{"currency": "USD", "rate": 200}], [{"stock": "AAPL", "price": 157}])
