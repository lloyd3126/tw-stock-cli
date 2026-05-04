"""Fetch TAIFEX options tick data for one trading date."""

import pandas as pd

from tw_stock_cli.crawlers.taifex.common import read_zipped_csv


def crawler(date: str) -> pd.DataFrame:
    url = (
        "https://www.taifex.com.tw/file/taifex/Dailydownload/"
        f"OptionsDailydownloadCSV/OptionsDaily_{date.replace('-', '_')}.zip"
    )
    return read_zipped_csv(url, encoding="big5hkscs", low_memory=False, skiprows=[1])


if __name__ == "__main__":
    df = crawler(date="2022-05-23")
    print(df)
