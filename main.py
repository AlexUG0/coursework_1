from src.services import simple_search
from src.utils import read_data
from src.views import get_main_page_data


def main():
    data_for_analysis = read_data()
    print("Введите дату и время в формате YYYY-MM-DD HH:MM:SS")
    user_date = input()
    print(get_main_page_data(data_for_analysis, user_date))
    print("Введите строку поиска")
    user_searching_string = input().lower()
    print(simple_search(user_searching_string))


if __name__ == "__main__":
    main()
