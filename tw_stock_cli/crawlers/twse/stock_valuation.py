"""Fetch TWSE PER, dividend yield, and price-to-book ratio data."""

import pandas as pd

from tw_stock_cli.crawlers.common import select_and_rename_columns
from tw_stock_cli.crawlers.twse.common import get_json
from tw_stock_cli.crawlers.twse.common import is_no_data


URL = "https://www.twse.com.tw/exchangeReport/BWIBBU_d?response=json&date={date}&selectType=ALL"
REFERER = "https://www.twse.com.tw/zh/trading/historical/bwibbu.html"
SOURCE_COLUMNS = [
    "證券代號",
    "證券名稱",
    "收盤價",
    "殖利率(%)",
    "股利年度",
    "本益比",
    "股價淨值比",
    "財報年/季",
]
OUTPUT_COLUMNS = [
    "stock_id",
    "stock_name",
    "close",
    "dividend_yield",
    "dividend_year",
    "per",
    "pbr",
    "financial_report_period",
]


def crawler(date: str) -> pd.DataFrame:
    payload = get_json(URL, date, REFERER)
    if is_no_data(payload):
        return pd.DataFrame()
    data = pd.DataFrame(list(payload["data"]), columns=payload["fields"])
    data = select_and_rename_columns(data, SOURCE_COLUMNS, OUTPUT_COLUMNS)
    data["date"] = date
    return data


if __name__ == "__main__":
    date = "2022-05-03"
    data = crawler(date)
    print(data)
