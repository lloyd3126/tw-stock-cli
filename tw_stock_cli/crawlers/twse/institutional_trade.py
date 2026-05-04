"""Fetch TWSE daily institutional investor buy and sell data."""

import pandas as pd
from loguru import logger

from tw_stock_cli.crawlers.twse.common import get_json
from tw_stock_cli.crawlers.twse.common import is_no_data


URL = "http://www.twse.com.tw/fund/T86?response=json&date={date}&selectType=ALLBUT0999"
REFERER = "http://www.twse.com.tw/zh/page/trading/fund/T86.html"
BUSY_STATUS = "很抱歉，目前線上人數過多，請您稍候再試"


def crawler(date: str) -> pd.DataFrame:
    payload = get_json(URL, date, REFERER)
    if is_no_data(payload):
        return pd.DataFrame()
    if payload.get("stat") == BUSY_STATUS:
        logger.warning(BUSY_STATUS)
        raise RuntimeError(BUSY_STATUS)
    return pd.DataFrame(payload["data"], columns=payload["fields"])


if __name__ == "__main__":
    date = "2022-04-12"
    df = crawler(date)
    print(df)
