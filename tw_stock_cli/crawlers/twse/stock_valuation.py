"""Fetch TWSE PER, dividend yield, and price-to-book ratio data."""

import pandas as pd

from tw_stock_cli.crawlers.twse.common import get_json
from tw_stock_cli.crawlers.twse.common import is_no_data


URL = "https://www.twse.com.tw/exchangeReport/BWIBBU_d?response=json&date={date}&selectType=ALL"
REFERER = "https://www.twse.com.tw/zh/trading/historical/bwibbu.html"


def crawler(date: str) -> pd.DataFrame:
    payload = get_json(URL, date, REFERER)
    if is_no_data(payload):
        return pd.DataFrame()
    data = pd.DataFrame(list(payload["data"]), columns=payload["fields"])
    data["date"] = date
    return data


if __name__ == "__main__":
    date = "2022-05-03"
    data = crawler(date)
    print(data)
