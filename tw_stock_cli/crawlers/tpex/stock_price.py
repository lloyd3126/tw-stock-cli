"""Fetch TPEx OTC securities daily open, high, low, and close quotes."""

import datetime
from typing import Any

import pandas as pd
import requests

from tw_stock_cli.crawlers.common import roc_date
from tw_stock_cli.crawlers.common import table_dataframe
from tw_stock_cli.crawlers.tpex.common import headers

URL = "https://www.tpex.org.tw/web/stock/aftertrading/otc_quotes_no1430/stk_wn1430_result.php?l=zh-tw&d={}&se=AL&_={}"
REFERER = "https://www.tpex.org.tw/web/stock/aftertrading/otc_quotes_no1430/stk_wn1430.php?l=zh-tw"

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

    resp = requests.get(
        url=URL.format(query_date, crawler_timestamp), headers=headers(REFERER)
    )
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
