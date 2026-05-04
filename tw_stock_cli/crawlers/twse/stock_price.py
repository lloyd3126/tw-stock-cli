"""Fetch TWSE listed securities daily open, high, low, and close quotes."""

import datetime
from typing import Any

import pandas as pd
import requests

from tw_stock_cli.crawlers.common import compact_date
from tw_stock_cli.crawlers.common import table_dataframe_by_field

URL = "https://www.twse.com.tw/rwd/zh/afterTrading/MI_INDEX?response=json&date={}&type=ALLBUT0999&_={}"
# TWSE after-trading endpoints expect browser-like request headers.
HEADER = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "keep-alive",
    "Host": "www.twse.com.tw",
    "Referer": "https://www.twse.com.tw/zh/page/trading/exchange/MI_INDEX.html",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "Windows",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
}
SOURCE_COLUMNS = ["證券代號", "證券名稱", "開盤價", "最高價", "最低價", "收盤價"]
OUTPUT_COLUMNS = ["stock_id", "stock_name", "open", "max", "min", "close"]


def crawler(parameters: dict[str, Any]) -> pd.DataFrame:
    crawler_date = str(parameters.get("crawler_date", ""))
    crawler_timestamp = int(datetime.datetime.now().timestamp())

    resp = requests.get(
        url=URL.format(compact_date(crawler_date), crawler_timestamp), headers=HEADER
    )
    if not resp.ok:
        return pd.DataFrame()
    data = table_dataframe_by_field(resp.json(), "證券代號")
    if data.empty:
        return pd.DataFrame()
    data = data[SOURCE_COLUMNS].copy()
    data.columns = OUTPUT_COLUMNS
    data["date"] = crawler_date
    return data


if __name__ == "__main__":
    parameters = {
        "crawler_date": "2022-01-26",
    }
    data = crawler(parameters)
    print(data)
