"""Fetch MOPS quarterly balance sheet summary tables."""

import typing
import requests

import pandas as pd
from loguru import logger
from crawler_common import html_tables


def header():
    return {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "mopsov.twse.com.tw",
        "Origin": "https://mopsov.twse.com.tw",
        "Referer": "https://mopsov.twse.com.tw/mops/web/t163sb05",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    }


def no_response(response: str) -> bool:
    if not response or "查無所需資料" in response:
        return True
    else:
        return False


def crawler(parameter: typing.Dict[str, str]) -> pd.DataFrame:
    logger.info(parameter)
    kind = parameter.get("kind", "sii")
    year = parameter.get("year", 111)
    quar = parameter.get("quar", 1)

    form_data = {
        "encodeURIComponent": "1",
        "step": "1",
        "firstin": "1",
        "off": "1",
        "isQuery": "Y",
        "TYPEK": kind,
        "year": year,
        "season": f"0{quar}",
    }
    url = "https://mopsov.twse.com.tw/mops/web/ajax_t163sb05"
    resp = requests.post(url, headers=header(), data=form_data)
    str_data = resp.text
    if no_response(str_data):
        df = pd.DataFrame()
    else:
        df = html_tables(str_data)
    return df

if __name__ == "__main__":
    # kind selects listed, OTC, emerging, or public-company statement tables.
    parameter = {"kind":"sii", "year":111, "quar":1}
    df = crawler(parameter)
    print(df)
