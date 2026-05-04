"""Fetch TAIFEX FCM futures trading volume for the night session."""

import pandas as pd

from tw_stock_cli.crawlers.taifex.common import fetch_fcm_csv


def crawler() -> pd.DataFrame:
    return fetch_fcm_csv("Daily_FUT_night.csv")


if __name__ == "__main__":
    df = crawler()
    print(df)
