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
        "Content-Type": "application/octet-stream;charset=UTF-8",
        "Host": "www.taifex.com.tw",
        "Origin": "https://www.taifex.com.tw",
        "Pragma": "no-cache",
        "Referer": "https://www.taifex.com.tw/cht/7/dailyFCM?menuid1=03",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36",
    }


def crawler():
    url = "https://www.taifex.com.tw/cht/7/getFCMFile?filename=Daily_FUT_night.csv"
    resp = requests.get(url=url, headers=header())
    if not resp.ok or not resp.content:
        logger.info("get request does not return valid content")
        return pd.DataFrame()

    df = pd.read_csv(io.StringIO(resp.content.decode("utf-8-sig"))).astype("str")
    df = df[df["期貨商代號"] != "Date"].reset_index(drop=True)
    return df


if __name__ == "__main__":
    df = crawler()
    print(df)
