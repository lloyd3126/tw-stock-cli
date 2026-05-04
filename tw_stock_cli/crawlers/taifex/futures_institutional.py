"""Fetch TAIFEX futures institutional investor positions and open interest."""

import io

import requests

import pandas as pd
from lxml import etree

from tw_stock_cli.crawlers.common import HTML_ACCEPT
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


def crawler_future(resp_text: str) -> pd.DataFrame:
    tables = pd.read_html(io.StringIO(resp_text))
    if not tables:
        return pd.DataFrame()
    df = tables[0]
    df.columns = [
        "_".join(
            str(part).strip() for part in col if not str(part).startswith("Unnamed")
        ).strip("_")
        if isinstance(col, tuple)
        else str(col).strip()
        for col in df.columns
    ]
    return df


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
