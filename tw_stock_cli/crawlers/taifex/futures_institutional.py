"""Fetch TAIFEX futures institutional investor positions and open interest."""

import io

import requests

import pandas as pd
from lxml import etree

from tw_stock_cli.crawlers.common import flatten_column_names
from tw_stock_cli.crawlers.common import HTML_ACCEPT
from tw_stock_cli.crawlers.common import rename_columns
from tw_stock_cli.crawlers.common import request_headers
from tw_stock_cli.crawlers.taifex.common import TAIFEX_ORIGIN


URL = "https://www.taifex.com.tw/cht/3/futContractsDate"
HEADERS = request_headers(
    accept=HTML_ACCEPT,
    referer=URL,
    origin=TAIFEX_ORIGIN,
    content_type="application/x-www-form-urlencoded",
    cache_control="no-cache",
    upgrade_insecure=True,
)
OUTPUT_COLUMNS = [
    "row_number",
    "contract_name",
    "investor_type",
    "trade_long_volume",
    "trade_long_amount",
    "trade_short_volume",
    "trade_short_amount",
    "trade_net_volume",
    "trade_net_amount",
    "open_interest_long_volume",
    "open_interest_long_amount",
    "open_interest_short_volume",
    "open_interest_short_amount",
    "open_interest_net_volume",
    "open_interest_net_amount",
]
COLUMN_MAP = {
    "序 號": "row_number",
    "商品 名稱": "contract_name",
    "身份別": "investor_type",
    "交易口數與契約金額_多方_口數": "trade_long_volume",
    "交易口數與契約金額_多方_契約 金額": "trade_long_amount",
    "交易口數與契約金額_空方_口數": "trade_short_volume",
    "交易口數與契約金額_空方_契約 金額": "trade_short_amount",
    "交易口數與契約金額_多空淨額_口數": "trade_net_volume",
    "交易口數與契約金額_多空淨額_契約 金額": "trade_net_amount",
    "未平倉餘額_多方_口數": "open_interest_long_volume",
    "未平倉餘額_多方_契約 金額": "open_interest_long_amount",
    "未平倉餘額_空方_口數": "open_interest_short_volume",
    "未平倉餘額_空方_契約 金額": "open_interest_short_amount",
    "未平倉餘額_多空淨額_口數": "open_interest_net_volume",
    "未平倉餘額_多空淨額_契約 金額": "open_interest_net_amount",
}


def crawler_future(resp_text: str) -> pd.DataFrame:
    tables = pd.read_html(io.StringIO(resp_text))
    if not tables:
        return pd.DataFrame()
    df = tables[0]
    df.columns = flatten_column_names(df.columns)
    return rename_columns(df, COLUMN_MAP)


def no_data(resp_text: str) -> bool:
    page = etree.HTML(resp_text)
    if page is None:
        return True
    temp = page.xpath('//td[@class="13red"]')
    messages = [(element.text or "").replace("\xa0", "") for element in temp]
    return "查無資料" in messages


def crawler(date: str) -> pd.DataFrame:
    form_data = {
        "queryType": "1",
        "goDay": "",
        "doQuery": "1",
        "dateaddcnt": "",
        "queryDate": date.replace("-", "/"),
    }
    resp = requests.post(
        url=URL,
        headers=HEADERS,
        data=form_data,
    )
    if no_data(resp.text):
        return pd.DataFrame()
    return crawler_future(resp_text=resp.text)


if __name__ == "__main__":
    df = crawler(date="2022-05-17")
    print(df)
