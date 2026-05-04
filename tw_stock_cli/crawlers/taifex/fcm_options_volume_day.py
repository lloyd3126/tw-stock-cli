"""Fetch TAIFEX FCM options trading volume for the regular session."""

import pandas as pd

from tw_stock_cli.crawlers.taifex.common import fetch_fcm_csv


def crawler() -> pd.DataFrame:
    return fetch_fcm_csv("Daily_OPT_day.csv")


if __name__ == "__main__":
    df = crawler()
    print(df)
