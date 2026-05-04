"""Fetch TWSE foreign and mainland China investor holding statistics."""

import pandas as pd
from loguru import logger

from tw_stock_cli.crawlers.common import rename_columns
from tw_stock_cli.crawlers.twse.common import get_json


URL = "http://www.twse.com.tw/fund/MI_QFIIS?response=json&date={date}&selectType=ALLBUT0999"
REFERER = "http://www.twse.com.tw/zh/page/trading/fund/MI_QFIIS.html"
OUTPUT_COLUMNS = [
    "stock_id",
    "stock_name",
    "isin",
    "issued_shares",
    "foreign_available_shares",
    "foreign_held_shares",
    "foreign_available_ratio",
    "foreign_held_ratio",
    "foreign_investment_limit_ratio",
    "mainland_investment_limit_ratio",
    "change_reason",
    "last_change_date",
]
COLUMN_MAP = {
    "證券代號": "stock_id",
    "證券名稱": "stock_name",
    "國際證券編碼": "isin",
    "發行股數": "issued_shares",
    "外資及陸資尚可投資股數": "foreign_available_shares",
    "全體外資及陸資持有股數": "foreign_held_shares",
    "外資及陸資尚可投資比率": "foreign_available_ratio",
    "全體外資及陸資持股比率": "foreign_held_ratio",
    "外資及陸資共用法令投資上限比率": "foreign_investment_limit_ratio",
    "陸資法令投資上限比率": "mainland_investment_limit_ratio",
    "與前日異動原因(註)": "change_reason",
    "最近一次上市公司申報外資及陸資持股異動日期": "last_change_date",
}


def crawler(date: str) -> pd.DataFrame:
    payload = get_json(URL, date, REFERER)
    if payload.get("stat") != "OK":
        logger.info(payload)
        return pd.DataFrame()
    data = pd.DataFrame(payload["data"], columns=payload["fields"])
    if data.empty:
        logger.info(payload)
        return pd.DataFrame()
    return rename_columns(data, COLUMN_MAP)


if __name__ == "__main__":
    df = crawler(date="2022-04-12")
    print(df)
