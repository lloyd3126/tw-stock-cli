"""Fetch TPEx index and total return index values for the requested month."""

import datetime
import requests

import pandas as pd
from loguru import logger
from tw_stock_cli.crawlers.common import table_dataframe


def crawler(date: str = "2019-01-01") -> pd.DataFrame:
    year = str(int(date.split("-")[0]) - 1911)
    date2 = "/".join([year] + date.split("-")[1:])
    url = "https://www.tpex.org.tw/web/stock/iNdex_info/reward_index/ROE_result.php?l=zh-tw&t=M&d={}".format(date2)
    response = requests.get(url)
    payload = response.json()
    df = table_dataframe(payload)
    if df.empty:
        return pd.DataFrame()

    df = df.rename(columns={"櫃買報酬指數(基期:94/12/30)": "櫃買報酬指數"})
    df["日期"] = df["日期"].apply(
        lambda d: datetime.datetime.strptime(
            str(int(d) + 19110000), "%Y%m%d"
        ).strftime("%Y-%m-%d")
    )
    return df


if __name__ == "__main__":
    date = "2022-04-12"
    df = crawler(date)
    print(df)
