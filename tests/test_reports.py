from src.reports import generation_reports, write_to_file


def test_generation_reports(test_dataframe):
    """Проверка корректности работы функции generation_reports,
    обернутой в декоратор write_to_file"""
    # atexit.register(generation_reports)
    assert generation_reports("Аптеки", "02.01.2021", test_dataframe) == [
        {"Дата операции": "02.01.2021", "Сумма операции": -500.0, "Категория": "Аптеки", "Описание": "Аптека Вита"}
    ]
