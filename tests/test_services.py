from pandas import DataFrame

from src.services import search_transfers


def test_search_transfers(test_dataframe: DataFrame) -> None:
    """Проверка корректности работы функции search_transfers"""
    assert (search_transfers(sorted_df=test_dataframe)) == (
        "[\n"
        "    {\n"
        '        "Дата операции": "04.01.2021",\n'
        '        "Сумма операции": -300.0,\n'
        '        "Категория": "Мобильная связь",\n'
        '        "Описание": "МТС Mobile +7 981 333-44-55"\n'
        "    },\n"
        "    {\n"
        '        "Дата операции": "12.01.2021",\n'
        '        "Сумма операции": -350.0,\n'
        '        "Категория": "Мобильная связь",\n'
        '        "Описание": "МегаФон +7 921 333-33-33"\n'
        "    }\n"
        "]"
    )
