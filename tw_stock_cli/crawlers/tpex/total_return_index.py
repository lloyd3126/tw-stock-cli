"""Fetch TPEx index and total return index values for the requested month."""

import datetime
import requests

import pandas as pd
from tw_stock_cli.crawlers.common import table_dataframe
from tw_stock_cli.crawlers.common import roc_date


URL = "https://www.tpex.org.tw/web/stock/iNdex_info/reward_index/ROE_result.php?l=zh-tw&t=M&d={date}"


def crawler(date: str = "2019-01-01") -> pd.DataFrame:
    response = requests.get(URL.format(date=roc_date(date)))
    payload = response.json()
    df = table_dataframe(payload)
    if df.empty:
        return pd.DataFrame()

    df = df.rename(
        columns={
            "日期": "date",
            "櫃買指數": "index",
            "櫃買報酬指數(基期:94/12/30)": "total_return_index",
        }
    )
    df["date"] = df["date"].apply(
        lambda d: datetime.datetime.strptime(str(int(d) + 19110000), "%Y%m%d").strftime(
            "%Y-%m-%d"
        )
    )
    return df


if __name__ == "__main__":
    date = "2022-04-12"
    df = crawler(date)
    print(df)
