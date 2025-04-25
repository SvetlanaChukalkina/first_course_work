from src.views import main

if __name__ == "__main__":
    to_date = input("Введите дату")
    param = input('Введите параметр')
    main_result = main(to_date, param)
    print(main_result)
