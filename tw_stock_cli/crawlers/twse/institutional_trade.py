"""Fetch TWSE daily institutional investor buy and sell data."""

import pandas as pd
from loguru import logger

from tw_stock_cli.crawlers.common import rename_columns
from tw_stock_cli.crawlers.twse.common import get_json
from tw_stock_cli.crawlers.twse.common import is_no_data


URL = "http://www.twse.com.tw/fund/T86?response=json&date={date}&selectType=ALLBUT0999"
REFERER = "http://www.twse.com.tw/zh/page/trading/fund/T86.html"
BUSY_STATUS = "很抱歉，目前線上人數過多，請您稍候再試"
OUTPUT_COLUMNS = [
    "stock_id",
    "stock_name",
    "foreign_ex_dealer_buy",
    "foreign_ex_dealer_sell",
    "foreign_ex_dealer_net_buy",
    "foreign_dealer_buy",
    "foreign_dealer_sell",
    "foreign_dealer_net_buy",
    "investment_trust_buy",
    "investment_trust_sell",
    "investment_trust_net_buy",
    "dealer_net_buy",
    "dealer_self_buy",
    "dealer_self_sell",
    "dealer_self_net_buy",
    "dealer_hedge_buy",
    "dealer_hedge_sell",
    "dealer_hedge_net_buy",
    "institutional_net_buy",
]
COLUMN_MAP = {
    "證券代號": "stock_id",
    "證券名稱": "stock_name",
    "外陸資買進股數(不含外資自營商)": "foreign_ex_dealer_buy",
    "外陸資賣出股數(不含外資自營商)": "foreign_ex_dealer_sell",
    "外陸資買賣超股數(不含外資自營商)": "foreign_ex_dealer_net_buy",
    "外資自營商買進股數": "foreign_dealer_buy",
    "外資自營商賣出股數": "foreign_dealer_sell",
    "外資自營商買賣超股數": "foreign_dealer_net_buy",
    "投信買進股數": "investment_trust_buy",
    "投信賣出股數": "investment_trust_sell",
    "投信買賣超股數": "investment_trust_net_buy",
    "自營商買賣超股數": "dealer_net_buy",
    "自營商買進股數(自行買賣)": "dealer_self_buy",
    "自營商賣出股數(自行買賣)": "dealer_self_sell",
    "自營商買賣超股數(自行買賣)": "dealer_self_net_buy",
    "自營商買進股數(避險)": "dealer_hedge_buy",
    "自營商賣出股數(避險)": "dealer_hedge_sell",
    "自營商買賣超股數(避險)": "dealer_hedge_net_buy",
    "三大法人買賣超股數": "institutional_net_buy",
}


def crawler(date: str) -> pd.DataFrame:
    payload = get_json(URL, date, REFERER)
    if is_no_data(payload):
        return pd.DataFrame()
    if payload.get("stat") == BUSY_STATUS:
        logger.warning(BUSY_STATUS)
        raise RuntimeError(BUSY_STATUS)
    data = pd.DataFrame(payload["data"], columns=payload["fields"])
    return rename_columns(data, COLUMN_MAP)


if __name__ == "__main__":
    date = "2022-04-12"
    df = crawler(date)
    print(df)
