import pandas as pd

from config import PATH_XLSX
from src.reports import generation_reports
from src.services import search_transfers
from src.utils import filter_operations
from src.views import main

if __name__ == "__main__":

    # Вывод по суммам трат и доходов за указанный период, а также курсов валют и акций
    to_date = input("Введите дату начала отсчета периода в формате ДД.ММ.ГГГГ")
    param = input(
        """Введите параметр для определения периода:
    "W" - с начала недели до указанной даты,
    "M" - с начала месяца до указанной даты,
    "Y" - с начала года до указанной даты,
    "ALL" - с начала 2000 года до указанной даты
    """
    )
    main_result = main(to_date, param)
    print(main_result)

    # Поиск транзакций, содержащих номер телефона
    new_to_date = input(
        """Введите дату начала отсчета периода в формате ДД.ММ.ГГГГ
        для поиска транзакций, содержащих номер телефона"""
    )
    new_param = input('Введите параметр для определения периода: "W", "M", "Y" или "ALL" ')
    sorted_df = filter_operations(param=new_param, to_date=new_to_date)
    transactions_with_phone_number = search_transfers(sorted_df)
    print(transactions_with_phone_number)

    # Траты за последние три месяца от выбранной даты
    selected_category = (input("Введите категорию для отображения трат за 3 месяца")).title()
    countdown_date = input("Введите дату начала отсчета периода в формате ДД.ММ.ГГГГ")
    transactions_df = pd.read_excel(PATH_XLSX)
    reports_result = generation_reports(selected_category, countdown_date, transactions_df)
    print("Результат записан в файл reports.json")
