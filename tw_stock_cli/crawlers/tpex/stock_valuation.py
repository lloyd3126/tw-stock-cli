"""Fetch TPEx PER, dividend yield, and price-to-book ratio data."""

import requests

import pandas as pd
from tw_stock_cli.crawlers.common import table_dataframe


def crawler(date: str = "2019-01-01") -> pd.DataFrame:
    year = str(int(date.split("-")[0]) - 1911)
    date2 = "/".join([year] + date.split("-")[1:])
    url = "https://www.tpex.org.tw/web/stock/aftertrading/peratio_analysis/pera_result.php?l=zh-tw&d={}".format(date2)
    response = requests.get(url)
    payload = response.json()
    data = table_dataframe(payload)
    if data.empty:
        return pd.DataFrame()

    data = data[["股票代號", "公司名稱", "本益比", "每股股利", "股利年度", "殖利率(%)", "股價淨值比"]]
    data.columns = [
        "stock_id",
        "stock_name",
        "PER",
        "dividend_per_share",
        "year",
        "dividend_yield",
        "PBR",
    ]

    data["date"] = date
    return data

if __name__ == "__main__":
    date = "2022-05-03"
    data = crawler(date)
    print(data)
