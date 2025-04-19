import datetime
import json
import logging
import os

import pandas as pd
import requests
from dotenv import load_dotenv

from config import DATA_FILE, PATH_HOME, USER_SETTINGS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename=os.path.join(PATH_HOME, "logs", "logs.log"),
    encoding="utf-8",
    filemode="w",
)
logger = logging.getLogger("utils")

path_to_dotenv = os.path.join(PATH_HOME, ".env")
load_dotenv(path_to_dotenv)


def read_data(patch=DATA_FILE):
    """Функция считывает данные о транзакциях из excel-файла"""
    try:
        df = pd.read_excel(patch)
        logger.info(f"Получены данные из файла {patch}")
        return df
    except FileNotFoundError:
        logger.error("Не найден путь к файлу")


def get_greeting():
    """Функция возвращает приветствие пользователя в зависимости от текущего времени"""
    current_date = datetime.datetime.now()
    current_hour = current_date.hour  # текущий час
    if 6 <= current_hour < 12:
        greeting = "Доброе утро!"
    elif 12 <= current_hour < 18:
        greeting = "Добрый день!"
    elif 18 <= current_hour < 24:
        greeting = "Добрый вечер!"
    else:
        greeting = "Доброй ночи!"
    logger.info("Приветствие выполнено")
    return greeting


def filter_data_by_user_date(date_for_filtering: str, df):
    """Функция возвращает данные с начала месяца, на который выпадает входящая дата, по входящую дату"""
    try:
        df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="mixed", dayfirst=True)
        # pattern = re.compile(r"\d+-\d+-\d+ \d+:\d+:\d+")
        # if pattern.match(date_for_filtering):
        date_up = datetime.datetime.strptime(date_for_filtering, "%Y-%m-%d %H:%M:%S")  # верхняя граница фильтрации
        date_low = date_up.replace(day=1, hour=0, minute=0, second=0)  # нижняя граница фильтрации
        filtered_transaction = df.loc[(df["Дата операции"] >= date_low) & (df["Дата операции"] < date_up)]
        logger.info(f"Получены отфильтрованные данные с {date_low} по {date_up}")
        return filtered_transaction
    except Exception as e:
        logger.error(f"Ошибка обработки данных {e}")


def get_info_by_card(df: pd.DataFrame):
    """Функция получает информацию о расходах по картам и кешбэк"""
    try:
        grouped_by_card = df.groupby("Номер карты").agg(
            total_spent=("Сумма платежа", lambda x: abs(round(x[x < 0].sum(), 2))),
            cashback=("Сумма платежа", lambda x: abs(round(x[x < 0].sum() * 0.01, 2))),
        )
        grouped_by_card.reset_index(names="last_digits", inplace=True)
        card_info = grouped_by_card.to_dict("records")
        logger.info("Получена информация о тратах по картам и расходах")
        return card_info
    except Exception as e:
        logger.error(f"Ошибка обработки данных {e}")


def get_top_transaction(df: pd.DataFrame):
    """Функция получает топ-5 транзакций по сумме платежа"""
    try:
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
    except Exception as e:
        logger.error(f"Ошибка обработки данных {e}")


def get_exchange_rate():
    """Функция получает информацию о курсе валют"""
    try:
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
        logger.info(f"Получены курсы валют {currencies}")
        return currencies_list
    except Exception as e:
        logger.error(f"Ошибка обработки данных {e}")


def get_stock_prices():
    """Функция получает информацию о стоимости акций"""
    try:
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
        logger.info(f"Получены данные о стоимости акций {tickers}")
        return stock_prices
    except Exception as e:
        logger.error(f"Ошибка обработки данных {e}")
