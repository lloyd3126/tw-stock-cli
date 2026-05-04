"""Fetch TAIFEX daily options market data."""

import pandas as pd

from tw_stock_cli.crawlers.taifex.common import fetch_daily_market_csv


URL = "https://www.taifex.com.tw/cht/3/dlOptDataDown"
REFERER = "https://www.taifex.com.tw/cht/3/dlOptDailyMarketView"


def crawler(date: str) -> pd.DataFrame:
    return fetch_daily_market_csv(URL, REFERER, date)


if __name__ == "__main__":
    df = crawler(date="2022-05-17")
    print(df)
