"""Fetch TWSE total return index values for the requested month."""

import pandas as pd

from tw_stock_cli.crawlers.twse.common import get_json
from tw_stock_cli.crawlers.twse.common import is_no_data


URL = "https://www.twse.com.tw/indicesReport/MFI94U?response=json&date={date}"
REFERER = "https://www.twse.com.tw/zh/indices/taiex/mi-5min-hist.html"


def crawler(date: str) -> pd.DataFrame:
    payload = get_json(URL, date, REFERER)
    if is_no_data(payload):
        return pd.DataFrame()
    columns = [column.replace("\u3000", "") for column in payload["fields"]]
    return pd.DataFrame(list(payload["data"]), columns=columns)


if __name__ == "__main__":
    date = "2022-04-12"
    df = crawler(date)
    print(df)
