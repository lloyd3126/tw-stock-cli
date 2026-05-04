"""Fetch TWSE daily margin purchase and short sale balances."""

import pandas as pd
from loguru import logger

from tw_stock_cli.crawlers.twse.common import get_json


URL = "http://www.twse.com.tw/exchangeReport/MI_MARGN?response=json&date={date}&selectType=ALL"
REFERER = "http://www.twse.com.tw/zh/page/trading/exchange/MI_MARGN.html"
OUTPUT_COLUMNS = [
    "股票代號",
    "股票名稱",
    "融資_買進",
    "融資_賣出",
    "融資_現金償還",
    "融資_前日餘額",
    "融資_今日餘額",
    "融資_次一營業日限額",
    "融券_買進",
    "融券_賣出",
    "融券_現券償還",
    "融券_前日餘額",
    "融券_今日餘額",
    "融券_次一營業日限額",
    "資券互抵",
    "註記",
]


def margin_rows(payload: dict) -> list:
    return payload["tables"][1]["data"] if "tables" in payload else payload["data"]


def crawler(date: str) -> pd.DataFrame:
    try:
        rows = margin_rows(get_json(URL, date, REFERER))
    except Exception as e:
        logger.error(e)
        return pd.DataFrame()

    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows, columns=OUTPUT_COLUMNS)


if __name__ == "__main__":
    df = crawler(date="2022-05-16")
    print(df)
