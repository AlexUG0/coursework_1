import json

from src.utils import get_top_transaction  # read_data,
from src.utils import filter_data_by_user_date, get_exchange_rate, get_greeting, get_info_by_card, get_stock_prices


def get_main_page_data(date, df):
    """ Функция для страницы "Главная" """
    filtered_df = filter_data_by_user_date(date, df)

    json_str = {
        "greeting": get_greeting(),
        "cards": get_info_by_card(filtered_df),
        "top_transactions": get_top_transaction(filtered_df),
        "currency_rates": get_exchange_rate(),
        "stock_prices": get_stock_prices(),
    }

    result = json.dumps(json_str, indent=4, ensure_ascii=False)
    return result

# data_for_analysis = read_data()
# user_date = "2021-11-23 12:53:01"  перевод
# print(get_main_page_data(user_date, data_for_analysis))
