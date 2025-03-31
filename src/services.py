import json


def simple_search(transactions_list, search_string):
    """Функция возвращает данные об операциях, содержащих в описании или категории искомую строку"""
    filtered_list = list(filter(lambda x:
        search_string in (str(x.get("Категория", "")).lower()) or
        search_string in (str(x.get("Описание", "")).lower()), transactions_list))
    return json.dumps(filtered_list, indent=4, ensure_ascii=False)
