from src.utils import data_expences, method_name, data_income, iter_user_settings


def main(to_date, param="M") -> None:
    """Запрос дат и вывод информации за указанный период"""
    sorted_date_excel = method_name(param, to_date)
    expences = data_expences(sorted_date_excel)
    income = data_income(sorted_date_excel)

    currency_rates, stocks_convert = iter_user_settings()



    answer = {
        "expenses": expences,
        "income": income,
        "currency_rates": currency_rates,
        "stock_prices": stocks_convert
    }

    print(answer)







