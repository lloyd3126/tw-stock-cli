"""Fetch TAIFEX futures institutional investor positions and open interest."""

import io

import requests

import pandas as pd
from lxml import etree


URL = "https://www.taifex.com.tw/cht/3/futContractsDate"
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Content-Length": "78",
    "Content-Type": "application/x-www-form-urlencoded",
    "Host": "www.taifex.com.tw",
    "Origin": "https://www.taifex.com.tw",
    "Pragma": "no-cache",
    "Referer": URL,
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
}


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
