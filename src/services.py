import json
import logging

logger = logging.getLogger("services")


def simple_search(transactions_list, search_string):
    """Функция возвращает данные об операциях, содержащих в описании или категории искомую строку"""
    try:
        filtered_list = list(
            filter(
                lambda x: search_string in (str(x.get("Категория", "")).lower())
                or search_string in (str(x.get("Описание", "")).lower()),
                transactions_list,
            )
        )
        logger.info(f"Получены данные операциях по строке {search_string}")
        return json.dumps(filtered_list, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Ошибка обработки данных {e}")
