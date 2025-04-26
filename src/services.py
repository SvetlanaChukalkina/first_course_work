import re
import json
import pandas as pd

from config import PATH_XLSX
from src.utils import excel_reader
df = excel_reader(path="../data/operations.xlsx")

def search_transfers(df:pd.DataFrame):
    """"Поиск транзакций, содаржащим в описании телефонные номера"""
    transfers_list = df.to_dict(orient="records")
    search_result = []
    pattern = re.compile(r'\d{2}-\d{2}-\d{2}')
    for i in transfers_list:
        if pattern.findall(i["Описание"]):
            search_result.append(i)
    # print(search_result)
    json_data = json.dump(search_result, indent=4, ensure_ascii=False)
    return(json_data)

search_transfers(df)
