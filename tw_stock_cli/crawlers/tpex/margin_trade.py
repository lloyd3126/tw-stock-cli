"""Fetch TPEx daily margin purchase and short sale balances."""

import pandas as pd
import requests
from loguru import logger

from tw_stock_cli.crawlers.common import table_dataframe
from tw_stock_cli.crawlers.common import roc_date
from tw_stock_cli.crawlers.tpex.common import headers


URL = "https://www.tpex.org.tw/web/stock/margin_trading/margin_balance/margin_bal_result.php?l=zh-tw&o=json&d={date}"
REFERER = "https://www.tpex.org.tw/web/stock/margin_trading/margin_balance/margin_bal.php?l=zh-tw"
OUTPUT_COLUMNS = [
    "stock_id",
    "stock_name",
    "margin_purchase_previous_balance",
    "margin_purchase_buy",
    "margin_purchase_sell",
    "margin_purchase_cash_repayment",
    "margin_purchase_balance",
    "margin_purchase_from_finance_company",
    "margin_purchase_usage_ratio",
    "margin_purchase_limit",
    "short_sale_previous_balance",
    "short_sale_sell",
    "short_sale_buy",
    "short_sale_stock_repayment",
    "short_sale_balance",
    "short_sale_from_finance_company",
    "short_sale_usage_ratio",
    "short_sale_limit",
    "offsetting_trade",
    "note",
]


def crawler(date: str) -> pd.DataFrame:
    if date < "2007-01-01":
        return pd.DataFrame()
    try:
        response = requests.get(
            url=URL.format(date=roc_date(date)), headers=headers(REFERER)
        )
        data = table_dataframe(response.json(), columns=OUTPUT_COLUMNS)
    except Exception as e:
        logger.error(e)
        return pd.DataFrame()

    if data.empty:
        return pd.DataFrame()
    return data


if __name__ == "__main__":
    df = crawler(date="2022-05-17")
    print(df)
