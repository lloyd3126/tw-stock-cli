import io
import typing
import requests

import pandas as pd
from loguru import logger


def header():
    return {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Length": "101",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "www.taifex.com.tw",
        "Origin": "https://www.taifex.com.tw",
        "Pragma": "no-cache",
        "Referer": "https://www.taifex.com.tw/cht/3/dlFutDailyMarketView",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36",
    }


def crawler(date:str) -> pd.DataFrame:
    url = "https://www.taifex.com.tw/cht/3/dlFutDataDown"
    form_data = {
        "down_type": "1",
        "commodity_id": "all",
        "queryStartDate": date.replace("-", "/"),
        "queryEndDate": date.replace("-", "/"),
    }
    resp = requests.post(url=url, headers=header(), data=form_data)
    if resp.ok:
        if resp.content:
            df = pd.read_csv(io.StringIO(resp.content.decode("big5")), index_col=False)
    else:
        return pd.DataFrame()
    return df


if __name__ == "__main__":
    df = crawler(date = "2022-05-17")
    print(df)
