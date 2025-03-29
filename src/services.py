import json

from src.utils import read_data


def simple_search(search_string):
    """Функция возвращает данные об операциях, содержащих в описании или категории искомую строку"""
    df = read_data()
    found_data = df.loc[(df["Категория"].str.contains(search_string)) | (df["Описание"].str.contains(search_string))]
    fd_json = found_data.to_json(orient="records", force_ascii=False)
    print(type(found_data))
    return json.dumps(fd_json, indent=4, ensure_ascii=False)
