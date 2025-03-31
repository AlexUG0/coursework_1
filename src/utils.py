import datetime
import json
import os
import re

import pandas as pd
import requests
from dotenv import load_dotenv

from config import DATA_FILE, PATH_HOME, USER_SETTINGS

path_to_dotenv = os.path.join(PATH_HOME, ".env")
load_dotenv(path_to_dotenv)


def read_data(patch=DATA_FILE):
    """Функция считывает данные о транзакциях из excel-файла"""
    df = pd.read_excel(patch)
    return df


def get_greeting():
    """Функция возвращает приветствие пользователя в зависимости от текущего времени"""
    current_hour = int(datetime.datetime.now().hour)  # текущий час
    if 6 <= current_hour < 12:
        greeting = "Доброе утро!"
    elif 12 <= current_hour < 18:
        greeting = "Добрый день!"
    elif 18 <= current_hour < 24:
        greeting = "Добрый вечер!"
    else:
        greeting = "Доброй ночи!"
    return greeting


def filter_data_by_user_date(date_for_filtering:str, df):
    """Функция возвращает данные с начала месяца, на который выпадает входящая дата, по входящую дату"""
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="mixed", dayfirst=True)
    pattern = re.compile(r"\d+-\d+-\d+ \d+:\d+:\d+")
    if pattern.match(date_for_filtering):
        date_up = datetime.datetime.strptime(date_for_filtering, "%Y-%m-%d %H:%M:%S")  # верхняя граница фильтрации
        date_low = date_up.replace(day=1, hour=0, minute=0, second=0)  # нижняя граница фильтрации
        filtered_transaction = df.loc[(df["Дата операции"] >= date_low) & (df["Дата операции"] < date_up)]
        return filtered_transaction
    else:
        raise ValueError


def get_info_by_card(df: pd.DataFrame):
    """Функция получает информацию о расходах по картам и кэшбеке"""
    grouped_by_card = df.groupby("Номер карты").agg(
        total_spent=("Сумма платежа", lambda x: abs(round(x[x < 0].sum(), 2))),
        cashback=("Сумма платежа", lambda x: abs(round(x[x < 0].sum() * 0.01, 2))),
    )
    grouped_by_card.reset_index(names="last_digits", inplace=True)
    card_info = grouped_by_card.to_dict("records")
    return card_info


def get_top_transaction(df: pd.DataFrame):
    """Функция получает топ-5 транзакций по сумме платежа"""
    top_transactions = df.sort_values(by="Сумма платежа", ascending=True).head(5)
    return [
        {
            "date": row["Дата операции"].strftime("%d.%m.%Y"),
            "amount": abs(round(row["Сумма платежа"], 2)),
            "category": row["Категория"],
            "description": row["Описание"],
        }
        for index, row in top_transactions.iterrows()
    ]


def get_exchange_rate():
    """Функция получает информацию о курсе валют"""
    currencies_list = []
    with open(USER_SETTINGS) as f:
        data = json.load(f)
        currencies = data["user_currencies"]
    for currency in currencies:
        apy_key = os.getenv("API_EX_RATE")
        url = f"https://api.apilayer.com/exchangerates_data/latest?symbols=RUB&base={currency}"
        payload = {}
        headers = {"apikey": apy_key}
        response = requests.request("GET", url, headers=headers, data=payload).json()
        currency_appending = {"currency": response["base"], "rate": response["rates"]["RUB"]}
        currencies_list.append(currency_appending)
    return currencies_list


def get_stock_prices():
    """Функция получает информацию о стоимости акций"""
    stock_prices = []
    with open(USER_SETTINGS) as f:
        data = json.load(f)
        tickers = data["user_stocks"]
    for ticker in tickers:
        apy_key = os.getenv("API_STOCKS")
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={apy_key}"
        received_data = requests.get(url).json()
        quote_data = received_data["Global Quote"]
        stock_info = {"stock": ticker, "price": float(quote_data["05. price"])}
        stock_prices.append(stock_info)
    return stock_prices
