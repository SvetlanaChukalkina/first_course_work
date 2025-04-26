# from src.services import search_transfers
from src.utils import excel_reader
from src.views import main
# datafreim = excel_reader(path="data/operations.xlsx")

if __name__ == "__main__":
    to_date = input("Введите дату")
    param = input('Введите параметр')
    main_result = main(to_date, param)
    # search_total_result = search_transfers()
    print(main_result)
    # print(search_total_result)
