import re
import json
import pandas as pd
from src.utils import excel_reader
df = excel_reader(path="../data/operations.xlsx")

def search_transfers(df:pd.DataFrame):
    """"Поиск по телефонным номерам"""
    transfers_list = df.to_dict(orient="records")
    search_result = []
    pattern = re.compile(r'\d{2}-\d{2}-\d{2}')
    for i in transfers_list:
        if pattern.findall(i["Описание"]):
            search_result.append(i)
    print(search_result)
    # json_data = json.dumps(search_result, w)
    # return(json_data)

search_transfers(df)
