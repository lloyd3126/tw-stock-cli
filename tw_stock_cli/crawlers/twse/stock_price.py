"""Fetch TWSE listed securities daily open, high, low, and close quotes."""

import datetime
from typing import Any

import pandas as pd
import requests

from tw_stock_cli.crawlers.common import compact_date
from tw_stock_cli.crawlers.common import select_and_rename_columns
from tw_stock_cli.crawlers.common import table_dataframe_by_field
from tw_stock_cli.crawlers.twse.common import headers

URL = "https://www.twse.com.tw/rwd/zh/afterTrading/MI_INDEX?response=json&date={}&type=ALLBUT0999&_={}"
REFERER = "https://www.twse.com.tw/zh/page/trading/exchange/MI_INDEX.html"
SOURCE_COLUMNS = ["證券代號", "證券名稱", "開盤價", "最高價", "最低價", "收盤價"]
OUTPUT_COLUMNS = ["stock_id", "stock_name", "open", "high", "low", "close"]


def crawler(parameters: dict[str, Any]) -> pd.DataFrame:
    crawler_date = str(parameters.get("crawler_date", ""))
    crawler_timestamp = int(datetime.datetime.now().timestamp())

    resp = requests.get(
        url=URL.format(compact_date(crawler_date), crawler_timestamp),
        headers=headers(REFERER),
    )
    if not resp.ok:
        return pd.DataFrame()
    data = table_dataframe_by_field(resp.json(), "證券代號")
    if data.empty:
        return pd.DataFrame()
    data = select_and_rename_columns(data, SOURCE_COLUMNS, OUTPUT_COLUMNS)
    data["date"] = crawler_date
    return data


if __name__ == "__main__":
    parameters = {
        "crawler_date": "2022-01-26",
    }
    data = crawler(parameters)
    print(data)
