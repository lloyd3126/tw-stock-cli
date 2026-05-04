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
    "代號",
    "名稱",
    "融資_前資餘額(張)",
    "融資_資買",
    "融資_資賣",
    "融資_現償",
    "融資_資餘額",
    "融資_資屬證金",
    "融資_資使用率(%)",
    "融資_資限額",
    "融券_前券餘額(張)",
    "融券_券賣",
    "融券_券買",
    "融券_券償",
    "融券_券餘額",
    "融券_券屬證金",
    "融券_券使用率(%)",
    "融券_券限額",
    "資券相抵(張)",
    "備註",
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
