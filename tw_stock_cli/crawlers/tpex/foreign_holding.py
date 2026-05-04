"""Fetch TPEx foreign investor holding ratio rankings."""

import pandas as pd
from tw_stock_cli.crawlers.common import table_dataframe
from tw_stock_cli.crawlers.tpex.common import get_json


URL = "https://www.tpex.org.tw/web/stock/3insti/qfii/qfii_result.php?l=zh-tw&d={date}"
REFERER = "https://www.tpex.org.tw/web/stock/3insti/qfii/qfii.php?l=zh-tw"
OUTPUT_COLUMNS = [
    "排行",
    "代號",
    "名稱",
    "發行股數(A)",
    "僑外資及陸資尚可投資股數",
    "僑外資及陸資持有股數",
    "僑外資及陸資尚可投資比率",
    "僑外資及陸資持有比率",
    "法令投資上限比率",
    "備註",
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
