"""Fetch TPEx daily institutional investor buy and sell data."""

import pandas as pd

from tw_stock_cli.crawlers.common import table_dataframe
from tw_stock_cli.crawlers.tpex.common import get_json


URL = "https://www.tpex.org.tw/web/stock/3insti/daily_trade/3itrade_hedge_result.php?l=zh-tw&se=EW&t=D&d={date}"
REFERER = (
    "https://www.tpex.org.tw/web/stock/3insti/daily_trade/3itrade_hedge.php?l=zh-tw"
)
COLNAMES = [
    "代號",
    "名稱",
    "外資及陸資(不含外資自營商)_買進股數",
    "外資及陸資(不含外資自營商)_賣出股數",
    "外資及陸資(不含外資自營商)_買賣超股數",
    "外資自營商_買進股數",
    "外資自營商_賣出股數",
    "外資自營商_買賣超股數",
    "外資及陸資_買進股數",
    "外資及陸資_賣出股數",
    "外資及陸資_買賣超股數",
    "投信_買進股數",
    "投信_賣出股數",
    "投信_買賣超股數",
    "自營商(自行買賣)_買進股數",
    "自營商(自行買賣)_賣出股數",
    "自營商(自行買賣)_買賣超股數",
    "自營商(避險)_買進股數",
    "自營商(避險)_賣出股數",
    "自營商(避險)_買賣超股數",
    "自營商_買進股數",
    "自營商_賣出股數",
    "自營商_買賣超股數",
    "三大法人買賣超股數合計",
]


def crawler(date: str) -> pd.DataFrame:
    if date < "2018-01-15":
        return pd.DataFrame()
    data = table_dataframe(get_json(URL, date, REFERER), columns=COLNAMES)
    if data.empty:
        return pd.DataFrame()
    return data


if __name__ == "__main__":
    df = crawler(date="2022-05-16")
    print(df)
