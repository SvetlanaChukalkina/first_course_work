import json
import logging
import re

import pandas as pd

services_logger = logging.getLogger()
services_file_handler = logging.FileHandler("../logs/logs.log", "w")
services_file_formatter = logging.Formatter("%(asctime)s %(filename)s %(levelname)s: %(message)s")
services_file_handler.setFormatter(services_file_formatter)
services_logger.addHandler(services_file_handler)
services_logger.setLevel(logging.DEBUG)


def search_transfers(sorted_df: pd.DataFrame):
    """ "Поиск транзакций, содаржащим в описании телефонные номера"""
    transfers_list = sorted_df.to_dict(orient="records").copy()
    search_result = []
    pattern = re.compile(r"\d{2}-\d{2}-\d{2}")
    for i in transfers_list:
        i["Дата операции"] = str(i["Дата операции"])
        if pattern.findall(i["Описание"]):
            search_result.append(i)
    if len(search_result) == 0:
        services_logger.info("No search results")
        return "Транзакций с номерами телефонов в указанный период не найдено"
    else:
        services_logger.info("The search was completed successfully, the results are converted to json")
        search_result_json = json.dumps(search_result, indent=4, ensure_ascii=False)
    return search_result_json
