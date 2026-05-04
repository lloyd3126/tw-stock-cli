"""Fetch TWSE foreign and mainland China investor holding statistics."""

import pandas as pd
from loguru import logger

from tw_stock_cli.crawlers.twse.common import get_json


URL = "http://www.twse.com.tw/fund/MI_QFIIS?response=json&date={date}&selectType=ALLBUT0999"
REFERER = "http://www.twse.com.tw/zh/page/trading/fund/MI_QFIIS.html"


def crawler(date: str) -> pd.DataFrame:
    payload = get_json(URL, date, REFERER)
    if payload.get("stat") != "OK":
        logger.info(payload)
        return pd.DataFrame()
    data = pd.DataFrame(payload["data"], columns=payload["fields"])
    if data.empty:
        logger.info(payload)
        return pd.DataFrame()
    return data


if __name__ == "__main__":
    df = crawler(date="2022-04-12")
    print(df)
