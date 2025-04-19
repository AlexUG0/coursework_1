from src.reports import spending_by_category
from src.services import simple_search
from src.utils import read_data
from src.views import get_main_page_data


def main():
    # Главная
    print("Введите дату и время в формате YYYY-MM-DD HH:MM:SS:")
    user_date = input()
    print(get_main_page_data(user_date, read_data()))

    # Сервисы
    print("Введите строку для поиска операций:")
    user_searching_string = input().lower()
    print(simple_search(read_data().to_dict(orient="records"), user_searching_string))

    # Отчеты
    print("Введите наименование категории для вывода расходов:")
    user_category = input().lower()
    print("и конечную дату трехмесячного периода в формате ГГГГ-ММ-ДД")
    user_date_1 = input()
    print(
        spending_by_category(read_data(), user_category, user_date_1).to_json(
            orient="records", indent=4, force_ascii=False
        )
    )


if __name__ == "__main__":
    main()
