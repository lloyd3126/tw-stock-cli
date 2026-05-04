"""Fetch TPEx daily institutional investor buy and sell data."""

import pandas as pd

from tw_stock_cli.crawlers.common import table_dataframe
from tw_stock_cli.crawlers.tpex.common import get_json


URL = "https://www.tpex.org.tw/web/stock/3insti/daily_trade/3itrade_hedge_result.php?l=zh-tw&se=EW&t=D&d={date}"
REFERER = (
    "https://www.tpex.org.tw/web/stock/3insti/daily_trade/3itrade_hedge.php?l=zh-tw"
)
OUTPUT_COLUMNS = [
    "stock_id",
    "stock_name",
    "foreign_ex_dealer_buy",
    "foreign_ex_dealer_sell",
    "foreign_ex_dealer_net_buy",
    "foreign_dealer_buy",
    "foreign_dealer_sell",
    "foreign_dealer_net_buy",
    "foreign_total_buy",
    "foreign_total_sell",
    "foreign_total_net_buy",
    "investment_trust_buy",
    "investment_trust_sell",
    "investment_trust_net_buy",
    "dealer_self_buy",
    "dealer_self_sell",
    "dealer_self_net_buy",
    "dealer_hedge_buy",
    "dealer_hedge_sell",
    "dealer_hedge_net_buy",
    "dealer_total_buy",
    "dealer_total_sell",
    "dealer_total_net_buy",
    "institutional_net_buy",
]


def crawler(date: str) -> pd.DataFrame:
    if date < "2018-01-15":
        return pd.DataFrame()
    data = table_dataframe(get_json(URL, date, REFERER), columns=OUTPUT_COLUMNS)
    if data.empty:
        return pd.DataFrame()
    return data


if __name__ == "__main__":
    df = crawler(date="2022-05-16")
    print(df)
