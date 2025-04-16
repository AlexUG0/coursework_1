import datetime
import json
import logging
import os
from datetime import date
from typing import Optional

import pandas as pd
from dateutil.relativedelta import relativedelta


def report_decorator(filename=None):
    """
    Декоратор для функций-отчетов, записывающий результат в файл.
    Результаты сохраняются в папку 'reports' в корневом каталоге проекта.
    Имя файла отчета включает имя функции, если имя файла не передано явно.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)

                if not os.path.exists("reports"):
                    os.makedirs("reports")

                if filename:
                    filepath = os.path.join("reports", filename)
                else:
                    base_filename = "{}_{}.json".format(
                        func.__name__, datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    )
                    filepath = os.path.join("reports", base_filename)

                with open(filepath, "w", encoding="utf-8") as f:
                    if isinstance(result, pd.DataFrame):
                        json.dump(result.to_dict(orient="records"), f, indent=2, ensure_ascii=False, default=str)
                    else:
                        json.dump(result, f, indent=2, ensure_ascii=False, default=str)

                logging.info(f"Отчет {func.__name__} записан в файл: {filepath}")
                return result
            except Exception as e:
                logging.exception(f"Ошибка при формировании отчета {func.__name__}: {e}")
                return pd.DataFrame({"error": [str(e)]})

        return wrapper

    return decorator


@report_decorator()
def spending_by_category(transactions: pd.DataFrame, category: str, date_: Optional[str] = None) -> pd.DataFrame:
    transactions["Дата операции"] = pd.to_datetime(
        transactions["Дата операции"], format="%d.%m.%Y %H:%M:%S", dayfirst=True
    ).dt.date
    # transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], format="mixed", dayfirst=True)
    if date_:
        date_up = datetime.datetime.strptime(date_, "%Y-%m-%d").date()
    else:
        date_up = date.today()
    date_low = date_up - relativedelta(months=3)
    filter_by_date_transaction = transactions.loc[
        (transactions["Дата операции"] >= date_low) & (transactions["Дата операции"] <= date_up)
    ]
    filtered_df = filter_by_date_transaction[
        (filter_by_date_transaction["Категория"].str.lower() == category)
        & (filter_by_date_transaction["Сумма платежа"] < 0)
    ]

    return filtered_df
