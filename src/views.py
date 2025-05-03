import json
from typing import Any

from src.utils import data_expences, data_income, filter_operations, iter_user_settings


def main(to_date: Any, param: str = "M"):
    """Запрос дат и вывод информации за указанный период"""
    sorted_date_excel = filter_operations(param, to_date)
    result_expences = data_expences(sorted_date_excel)
    result_income = data_income(sorted_date_excel)

    currency_rates, stocks_convert = iter_user_settings()

    answer = {
        "expenses": result_expences,
        "income": result_income,
        "currency_rates": currency_rates,
        "stock_prices": stocks_convert,
    }
    answer_json = json.dumps(answer, indent=4, ensure_ascii=False)

    return answer_json
