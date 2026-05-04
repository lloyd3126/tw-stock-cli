"""Fetch TPEx foreign investor holding ratio rankings."""

import pandas as pd
from tw_stock_cli.crawlers.common import table_dataframe
from tw_stock_cli.crawlers.tpex.common import get_json


URL = "https://www.tpex.org.tw/web/stock/3insti/qfii/qfii_result.php?l=zh-tw&d={date}"
REFERER = "https://www.tpex.org.tw/web/stock/3insti/qfii/qfii.php?l=zh-tw"
OUTPUT_COLUMNS = [
    "rank",
    "stock_id",
    "stock_name",
    "issued_shares",
    "foreign_available_shares",
    "foreign_held_shares",
    "foreign_available_ratio",
    "foreign_held_ratio",
    "foreign_investment_limit_ratio",
    "note",
]


def crawler(date: str) -> pd.DataFrame:
    payload = get_json(URL, date, REFERER)
    data = table_dataframe(payload, columns=OUTPUT_COLUMNS)
    if data.empty:
        return pd.DataFrame()
    return data


if __name__ == "__main__":
    df = crawler(date="2022-05-16")
    print(df)
