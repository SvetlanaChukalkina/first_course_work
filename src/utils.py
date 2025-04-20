import pandas as pd

def excel_reader(path: str) -> list[dict]:
    """Cчитывает данные из Excel-файла"""
    try:
        excel_data = pd.read_excel(path)
        return excel_data
    except FileNotFoundError:
        return []

print(excel_reader(path="../data/operations.xlsx"))