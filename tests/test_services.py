import json

from src.services import simple_search


def test_simple_search_found(df_for_tests):
    search_string = "супермаркет"
    expected_filtered_list = [
        {
            "Дата операции": "31.12.2021 16:44:00",
            "Номер карты": "*7197",
            "Категория": "Супермаркеты",
            "Сумма платежа": -160.89,
            "Описание": "Колхоз",
        },
        {
            "Дата операции": "31.12.2021 15:44:39",
            "Номер карты": "*7197",
            "Категория": "Супермаркеты",
            "Сумма платежа": -78.05,
            "Описание": "Колхоз",
        },
    ]
    expected_json = json.dumps(expected_filtered_list, indent=4, ensure_ascii=False)
    transactions_list = df_for_tests.to_dict("records")
    result = simple_search(transactions_list, search_string)
    assert result == expected_json


def test_simple_search_not_found(df_for_tests):
    search_string = "авиабилеты"
    expected_filtered_list = []
    expected_json = json.dumps(expected_filtered_list, indent=4, ensure_ascii=False)
    transactions_list = df_for_tests.to_dict("records")
    result = simple_search(transactions_list, search_string)
    assert result == expected_json
