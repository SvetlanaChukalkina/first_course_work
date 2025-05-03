import datetime
import json
import logging
from typing import Optional

import pandas as pd

reports_logger = logging.getLogger()
reports_file_handler = logging.FileHandler("../logs/logs.log", "w")
reports_file_formatter = logging.Formatter("%(asctime)s %(filename)s %(levelname)s: %(message)s")
reports_file_handler.setFormatter(reports_file_formatter)
reports_logger.addHandler(reports_file_handler)
reports_logger.setLevel(logging.DEBUG)


def write_to_file(func):
    def wrapper(*args, **kwargs):
        formatted_file = json.dumps(func(*args, **kwargs), indent=4, ensure_ascii=False)
        with open("reports.json", "w", encoding="UTF-8") as json_file:
            json_file.write(formatted_file)

    return wrapper


@write_to_file
def generation_reports(selected_category: str = None, countdown_date: Optional[str] = None, transactions_df=None):
    if countdown_date is None:
        countdown_date_formatted = datetime.datetime.now()
        reports_logger.info("Date changed to the current one")
    else:
        countdown_date_formatted = datetime.datetime.strptime(countdown_date, "%d.%m.%Y")
        reports_logger.info("Date converted")
    end_date = countdown_date_formatted - datetime.timedelta(days=90)
    reports_logger.info("The end date of the period has been determined")

    transactions_df["Дата операции"] = pd.to_datetime(transactions_df["Дата операции"], dayfirst=True)
    transactions_for_date = transactions_df[
        (transactions_df["Дата операции"] <= countdown_date_formatted) & (transactions_df["Дата операции"] >= end_date)
    ].copy()
    transactions_for_date["Дата операции"] = transactions_for_date["Дата операции"].dt.strftime("%d.%m.%Y")
    transactions_for_date_formatted = transactions_for_date.to_dict(orient="records")
    transactions_filtered_by_category = []
    for transaction in transactions_for_date_formatted:
        if transaction["Категория"] == selected_category:
            transactions_filtered_by_category.append(transaction)
    if len(transactions_filtered_by_category) == 0:
        reports_logger.info("No search results")
        return "Транзакций по указанной категории за выбранный период не найдено"
    else:
        reports_logger.info("The search was completed successfully")
        return transactions_filtered_by_category
