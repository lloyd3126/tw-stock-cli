import ssl

import pandas as pd
from loguru import logger


def header():
    return {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Host": "www.taifex.com.tw",
        "Pragma": "no-cache",
        "Referer": "https://www.taifex.com.tw/cht/3/futDailyMarketReport",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    }


def crawler(date:str) -> pd.DataFrame:
    try:
        ssl._create_default_https_context = ssl._create_unverified_context
        data = pd.read_csv(
            "https://www.taifex.com.tw/file/taifex/Dailydownload/DailydownloadCSV/Daily_{}.zip".format(date.replace("-", "_")),
            encoding="big5hkscs",
            low_memory=False,
        )
    except BaseException:
        return pd.DataFrame()
    if len(data) == 0:
        return pd.DataFrame()
    return data


if __name__ == "__main__":
    df = crawler(date="2022-05-23")
    print(df)