import pytest
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

from src.reports import spending_by_category

def test_spending_by_category_with_date_limitation(df_for_tests):
    result = spending_by_category(df_for_tests, 'супермаркеты', '2021-12-31')
    assert len(result) == 2
    assert result['Сумма платежа'].sum() == -238.94
