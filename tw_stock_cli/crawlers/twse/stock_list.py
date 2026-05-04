"""Fetch TWSE listed security codes and names for a trading date."""

import pandas as pd

from tw_stock_cli.crawlers.common import compact_date
from tw_stock_cli.crawlers.common import get_json
from tw_stock_cli.crawlers.common import table_dataframe_by_field


URL = "https://www.twse.com.tw/rwd/zh/afterTrading/MI_INDEX?response=json&date={date}&type=ALLBUT0999"


def crawler(date: str) -> pd.DataFrame:
    payload = get_json(URL.format(date=compact_date(date)))
    data = table_dataframe_by_field(payload, "證券代號")
    if data.empty:
        return pd.DataFrame()
    data = data[["證券代號", "證券名稱"]].copy()
    data.columns = ["stock_id", "stock_name"]
    data["date"] = date
    return data


if __name__ == "__main__":
    date = "2022-05-05"
    data = crawler(date)
    print(data)
