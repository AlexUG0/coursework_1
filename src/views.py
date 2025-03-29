import json

from src.utils import (
    filter_data_by_user_date,
    get_exchange_rate,
    get_greeting,
    get_info_by_card,
    get_stock_prices,
    get_top_transaction,
)


def get_main_page_data(date, df):
    filtered_df = filter_data_by_user_date(date, df)

    json_str = {
        "greeting": get_greeting(),
        "cards": get_info_by_card(filtered_df),
        "top_transactions": get_top_transaction(filtered_df),
        "currency_rates": get_exchange_rate(),
        "stock_prices": get_stock_prices(),
    }
    result = json.dumps(json_str, indent=4)
    return result
