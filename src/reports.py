import datetime
from typing import Optional

from dateutil.relativedelta import relativedelta

import pandas as pd

from src.utils import read_data


def spending_by_category(transactions: pd.DataFrame,
                         category: str,
                         date: Optional[str] = None) -> pd.DataFrame:
    transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], format="mixed",
                                                   dayfirst=True)
    if date:
        date_up = datetime.datetime.strptime(date, "%Y-%m-%d")
    else:
        date_up = date.today()
    date_low = date_up - relativedelta(months=3)
    filter_by_date_transaction = transactions.loc[
        (transactions["Дата операции"] >= date_low) & (transactions["Дата операции"] <= date_up)]
    filtered_df = filter_by_date_transaction[
        (filter_by_date_transaction['Категория'] == category) & (filter_by_date_transaction['Сумма операции'] < 0)]

    return filtered_df
