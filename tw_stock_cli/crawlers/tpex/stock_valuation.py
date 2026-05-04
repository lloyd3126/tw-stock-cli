"""Fetch TPEx PER, dividend yield, and price-to-book ratio data."""

import requests

import pandas as pd
from tw_stock_cli.crawlers.common import select_and_rename_columns
from tw_stock_cli.crawlers.common import table_dataframe
from tw_stock_cli.crawlers.common import roc_date


URL = "https://www.tpex.org.tw/web/stock/aftertrading/peratio_analysis/pera_result.php?l=zh-tw&d={date}"
SOURCE_COLUMNS = [
    "股票代號",
    "公司名稱",
    "本益比",
    "每股股利",
    "股利年度",
    "殖利率(%)",
    "股價淨值比",
]
OUTPUT_COLUMNS = [
    "stock_id",
    "stock_name",
    "per",
    "dividend_per_share",
    "dividend_year",
    "dividend_yield",
    "pbr",
]


def crawler(date: str = "2019-01-01") -> pd.DataFrame:
    response = requests.get(URL.format(date=roc_date(date)))
    payload = response.json()
    data = table_dataframe(payload)
    if data.empty:
        return pd.DataFrame()

    data = select_and_rename_columns(data, SOURCE_COLUMNS, OUTPUT_COLUMNS)
    data["date"] = date
    return data


if __name__ == "__main__":
    date = "2022-05-03"
    data = crawler(date)
    print(data)
