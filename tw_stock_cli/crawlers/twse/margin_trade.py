"""Fetch TWSE daily margin purchase and short sale balances."""

import pandas as pd
from loguru import logger

from tw_stock_cli.crawlers.twse.common import get_json


URL = "http://www.twse.com.tw/exchangeReport/MI_MARGN?response=json&date={date}&selectType=ALL"
REFERER = "http://www.twse.com.tw/zh/page/trading/exchange/MI_MARGN.html"
OUTPUT_COLUMNS = [
    "stock_id",
    "stock_name",
    "margin_purchase_buy",
    "margin_purchase_sell",
    "margin_purchase_cash_repayment",
    "margin_purchase_previous_balance",
    "margin_purchase_balance",
    "margin_purchase_next_limit",
    "short_sale_buy",
    "short_sale_sell",
    "short_sale_stock_repayment",
    "short_sale_previous_balance",
    "short_sale_balance",
    "short_sale_next_limit",
    "offsetting_trade",
    "note",
]


def margin_rows(payload: dict) -> list:
    return payload["tables"][1]["data"] if "tables" in payload else payload["data"]


def crawler(date: str) -> pd.DataFrame:
    try:
        rows = margin_rows(get_json(URL, date, REFERER))
    except Exception as e:
        logger.error(e)
        return pd.DataFrame()

    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows, columns=OUTPUT_COLUMNS)


if __name__ == "__main__":
    df = crawler(date="2022-05-16")
    print(df)
