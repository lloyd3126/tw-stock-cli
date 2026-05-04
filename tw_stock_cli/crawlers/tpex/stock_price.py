"""Fetch TPEx OTC securities daily open, high, low, and close quotes."""

import datetime
from typing import Any

import pandas as pd
import requests

from tw_stock_cli.crawlers.common import roc_date
from tw_stock_cli.crawlers.common import table_dataframe

URL = "https://www.tpex.org.tw/web/stock/aftertrading/otc_quotes_no1430/stk_wn1430_result.php?l=zh-tw&d={}&se=AL&_={}"

# TPEx quote endpoints expect browser-like request headers.
HEADER = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "keep-alive",
    "Host": "www.tpex.org.tw",
    "Referer": "https://www.tpex.org.tw/web/stock/aftertrading/otc_quotes_no1430/stk_wn1430.php?l=zh-tw",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "Windows",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
}


COLNAMES = [
    "stock_id",
    "stock_name",
    "close",
    "open",
    "max",
    "min",
]
SOURCE_COLUMNS = ["代號", "名稱", "收盤 ", "開盤 ", "最高 ", "最低"]


def crawler(parameters: dict[str, Any]) -> pd.DataFrame:
    query_date = roc_date(str(parameters.get("crawler_date", "")))
    crawler_timestamp = int(datetime.datetime.now().timestamp())

    resp = requests.get(url=URL.format(query_date, crawler_timestamp), headers=HEADER)
    if not resp.ok:
        return pd.DataFrame()
    data = table_dataframe(resp.json())
    if data.empty:
        return pd.DataFrame()
    data = data[SOURCE_COLUMNS].copy()
    data.columns = COLNAMES
    data["date"] = parameters.get("crawler_date", "")
    return data


if __name__ == "__main__":
    parameters = {
        "crawler_date": "2022-01-26",
    }
    data = crawler(parameters)
    print(data)
