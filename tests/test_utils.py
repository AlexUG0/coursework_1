import json
import unittest
from unittest.mock import MagicMock, patch

import requests_mock
from freezegun import freeze_time

from src.utils import (filter_data_by_user_date, get_exchange_rate, get_greeting, get_info_by_card, get_stock_prices,
                       get_top_transaction, read_data)


@patch("pandas.read_excel")
def test_read_data(mock_read):
    mock_read.return_value = {"col1": [1, 2], "col2": [3, 4]}
    assert read_data("test_patch") == {"col1": [1, 2], "col2": [3, 4]}
    mock_read.assert_called_once_with("test_patch")


class TestFunctions(unittest.TestCase):

    def test_get_greeting(self):
        """Тест для функции get_greeting"""
        with freeze_time("2025-01-23 08:00:00"):
            self.assertEqual(get_greeting(), "Доброе утро!")
        with freeze_time("2025-01-23 15:00:00"):
            self.assertEqual(get_greeting(), "Добрый день!")
        with freeze_time("2025-01-23 18:00:00"):
            self.assertEqual(get_greeting(), "Добрый вечер!")
        with freeze_time("2025-01-23 00:00:00"):
            self.assertEqual(get_greeting(), "Доброй ночи!")


def test_filter_data_by_user_date(df_for_tests):
    result = filter_data_by_user_date("2021-12-30 17:52:30", df_for_tests)
    assert len(result) == 1


def test_get_info_by_card(df_for_tests):
    assert (get_info_by_card(df_for_tests)) == [
        {"last_digits": "*4556", "total_spent": 0.0, "cashback": 0.0},
        {"last_digits": "*5091", "total_spent": 564.0, "cashback": 5.64},
        {"last_digits": "*7197", "total_spent": 240.26, "cashback": 2.4},
    ]


def test_get_top_transaction(df_with_datetime_for_tests):
    assert len(get_top_transaction(df_with_datetime_for_tests)) == 5


def test_get_exchange_rate():
    settings_data = {"user_currencies": ["USD", "EUR"]}
    mock_file_handle = MagicMock()
    mock_file_handle.__enter__.return_value.read.return_value = json.dumps(settings_data)
    with (
        patch("builtins.open", return_value=mock_file_handle),
        patch("src.utils.os.getenv", return_value="test_api_key"),
        requests_mock.Mocker() as req_m,
    ):
        usd_response = {"base": "USD", "rates": {"RUB": 80}}
        eur_response = {"base": "EUR", "rates": {"RUB": 90}}
        req_m.get(
            "https://api.apilayer.com/exchangerates_data/latest?symbols=RUB&base=USD",
            json=usd_response,
        )
        req_m.get(
            "https://api.apilayer.com/exchangerates_data/latest?symbols=RUB&base=EUR",
            json=eur_response,
        )
        result = get_exchange_rate()
        expected_result = [{"currency": "USD", "rate": 80}, {"currency": "EUR", "rate": 90}]
        assert result == expected_result


def test_get_stock_prices():
    settings_data = {"user_stocks": ["AAPL", "GOOG"]}
    fake_responses = {
        "AAPL": {"Global Quote": {"05. price": "150.50"}},
        "GOOG": {"Global Quote": {"05. price": "2500.00"}},
    }

    mock_file_read = MagicMock()
    file_context_manager = MagicMock()
    file_context_manager.read.return_value = json.dumps(settings_data)
    mock_file_read.return_value = file_context_manager
    mock_file_read.return_value.__enter__.return_value = file_context_manager
    mock_file_read.return_value.__exit__ = lambda *args: None

    def fake_request(*args, **kwargs):
        url = args[0]
        ticker = url.split("&symbol=")[1].split("&")[0]
        return MagicMock(json=lambda: fake_responses[ticker])

    with patch("builtins.open", mock_file_read):
        with patch("src.utils.os.getenv", return_value="FAKE_API_KEY"):
            with patch("src.utils.requests.get", side_effect=fake_request):
                # Вызываем тестируемую функцию
                result = get_stock_prices()
                expected_result = [{"stock": "AAPL", "price": 150.50}, {"stock": "GOOG", "price": 2500.00}]
                assert result == expected_result
